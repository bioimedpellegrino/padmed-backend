from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.http import HttpResponseRedirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from codicefiscale import codicefiscale
from deepaffex.api import register_device, login, get_studies_by_id, get_studies_list, select_study, get_measurements_list, get_measurement, retrieve_sdk_config, make_measure #async
from deepaffex.utils import save_config, load_config
import asyncio
import datetime
import os
import json
import time

from app.models import AppUser
from .forms import PatientForm
from .models import Hospital, Patient, TriageCode, TriageAccessReason, TriageAccess, \
    PatientVideo, PatientMeasureResult, MeasureLogger, Totem
from .utils import generate_video_measure, unpack_result_deepaffex

class TestDFXApiView(APIView):
    """[summary]

        Args:
            request ([type]): [description]
    """
    def get(self, request, *args, **kwargs):
        
        response = asyncio.run(register_device())
        
        return Response(response, status=status.HTTP_200_OK)
    
class ReceptionsView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    TEMPLATE_NAME = 'receptions-access.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        
        form = PatientForm()
        user = AppUser.get_or_create_from_parent(request.user)
        return render(request, self.TEMPLATE_NAME, {'form': form, 'user': user})
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        user = AppUser.get_or_create_from_parent(request.user)
        totem = user.totem_logged
        if not totem:
            raise PermissionDenied("Solo gli utenti Totem sono abilitati all'inserimento dei dati. Effettura il login con un utente Totem o contattare l'assistenza.")
        hospital = totem.hospital

        
        if not hospital:
            raise PermissionDenied("Questo Totem non ha un hospedale associato. Associare un ospedale al Totem o contattare l'assistenza.")

        form = PatientForm(request.POST)
        
        if form.is_valid():
            fiscal_code = str(form.cleaned_data['fiscal_code']).upper()
            fiscal_code_decoded = codicefiscale.decode(fiscal_code)
            patient, created = Patient.objects.get_or_create(
                fiscal_code=fiscal_code_decoded['code']
                )
            patient_user, c = AppUser.objects.get_or_create(
                username=fiscal_code_decoded['code'],
                patient_logged=patient,
                )
            
            hospital = Hospital.objects.all().first() #TODO
            totem = Totem.objects.all().first() #TODO
            
            access = TriageAccess()
            access.patient = patient
            access.hospital = hospital
            access.totem = totem
            access.access_date = datetime.datetime.now()
            access.save()
            return HttpResponseRedirect(reverse('accessreason',kwargs={"access_id":access.id}))
        else:
            # TODO
            form = PatientForm()
            return render(request, self.TEMPLATE_NAME, {'form': form, 'errors': 'Il codice fiscale inserito non è valido', 'user': user})
        
class ReceptionsReasonsView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    
    TEMPLATE_NAME = 'receptions-accessreason.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        
        access_id = int(kwargs.get('access_id', None))
        access = get_object_or_404(TriageAccess,pk=access_id)
        
        reasons = TriageAccessReason.objects.filter(hospital=access.hospital) #TODO: filter by "enable" (to be defined)

        return render(request, self.TEMPLATE_NAME, {'access_id': access_id, 'reasons': reasons})
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        access_id = kwargs.get('access_id', None)
        access = get_object_or_404(TriageAccess,pk=access_id)
        
        reason_id = int(request.POST["reason_id"][0])
        reason = get_object_or_404(TriageAccessReason,pk=reason_id)
        
        access.access_reason = reason
        access.triage_code = reason.related_code
        access.save()
        
        return HttpResponseRedirect(reverse('record_video',kwargs={"access_id":access_id}))
    
class RecordVideoView(APIView):
    """
    Args:
        APIView ([type]): [description]
    """
    TEMPLATE_NAME = "receptions-videomeasuring.html"
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        
        access_id = kwargs.get('access_id', None)
        access = get_object_or_404(TriageAccess,pk=access_id)
        
        return render(request, self.TEMPLATE_NAME, {'access_id': access_id })
    
    parser_classes = (MultiPartParser,)
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):

        video = request.FILES['video']
        access_id = kwargs.get('access_id')
        triage_access = TriageAccess.objects.get(pk=access_id)

        file_path = default_storage.save('tmp/' + "{}.webm".format(access_id), video)

        video = generate_video_measure(file_path, access_id)
        
        patient_video = PatientVideo()
        patient_video.triage_access = triage_access
        patient_video.video = video
        patient_video.save()
        #Make the measure
        video_path = os.path.join(settings.MEDIA_ROOT, video)
        config_path = os.path.join(settings.CORE_DIR, "config.json")
        config = load_config(config_path)
        measurement_id, logs = asyncio.run(make_measure(config=config, config_path=config_path, video_path=video_path))
        # Logger
        log = MeasureLogger()
        log.triage_access = triage_access
        log.log = json.dumps(logs)
        log.save()
        # Save results
        p_measure_result = PatientMeasureResult()
        p_measure_result.patient_video = patient_video
        p_measure_result.measurement_id = measurement_id
        # Retrive comprehensive measurement informations
        time.sleep(2)
        result = asyncio.run(get_measurement(config=config, measurement_id=measurement_id))
        p_measure_result.result = result
        p_measure_result.save()
        p_measure_result.measure_short = unpack_result_deepaffex(result)
        p_measure_result.save()
        
        return Response({'p_measure_result': p_measure_result.pk }, status=status.HTTP_200_OK)
    
class PatientResults(APIView):
    """
    Args:
        ApiView ([type]): [description]
    """
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        patient_result = PatientMeasureResult.objects.get(pk=int(request.POST.get('p_measure_result')))
        measure = eval(patient_result.measure_short)
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        return render(request,'receptions-results.html', {'measure': measure, 'date': today_date})

class TestNFC(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):

        return render(request,'testnfc.html', {'show_arrow': True})
    
class UserConditions(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        
        user = None
        
        try:
            user = AppUser.get_or_create_from_parent(request.user)
        except:
            pass
        
        return render(request,'receptions-conditions.html', {'user': user}) # receptions-conditions.html
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        user = None
        
        try:
            user = AppUser.get_or_create_from_parent(request.user)
        except:
            pass
        
        return HttpResponseRedirect(reverse('receptions'))