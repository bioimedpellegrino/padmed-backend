from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.conf import settings

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

from .forms import PatientForm
from .models import Hospital, Patient, TriageCode, TriageAccessReason, TriageAccess, PatientVideo, PatientMeasureResult
from .utils import generate_video_measure

class DecodeFiscalCodeView(APIView):
    """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
    """
    def post(self, request, *args, **kwargs):
        
        return Response(
            codicefiscale.decode(request.data['fiscal_code']), 
            status=status.HTTP_200_OK)
        

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
    template_name = 'receptions-access.html'
    
    def get(self, request, *args, **kwargs):
        
        form = PatientForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        
        form = PatientForm(request.POST)
        
        if form.is_valid():
            fiscal_code = str(form.cleaned_data['fiscal_code']).upper()
            fiscal_code_decoded = codicefiscale.decode(fiscal_code)
            user, c = User.objects.get_or_create(username=fiscal_code_decoded['code'])
            patient, created = Patient.objects.get_or_create(fiscal_code=fiscal_code_decoded['code'], user=user)
            hospital = Hospital.objects.all().first()
            
            if created:
                patient.birth_date = fiscal_code_decoded['birthdate']
                patient.gender = fiscal_code_decoded['sex']
                patient.birth_place = fiscal_code_decoded['birthplace']['name']
                patient.save()
            
            access = TriageAccess()
            access.patient = patient
            access.hospital = hospital
            access.access_date = datetime.datetime.now()
            access.save()
            
            reasons = TriageAccessReason.objects.filter(hospital=hospital)
            res = [{ 'label': reason.reason, 'id': reason.id } for reason in reasons]
            return render(request, 'receptions-accessreason.html', {'access_id': access.id, 'reasons': res})
        else:
            form = PatientForm()
            return render(request, self.template_name, {'form': form, 'errors': 'Il codice fiscale inserito non è valido'})
        
class ReceptionsReasonsView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'receptions-accessreason.html'
    
    def get(self, request, *args, **kwargs):
        
        access_id = kwargs.get('access_id', None)
        reason_id = kwargs.get('reason_id', None)

        access = TriageAccess.objects.get(pk=access_id)
        reason = TriageAccessReason.objects.get(pk=reason_id)
        
        access.access_reason = reason
        access.triage_code = reason.related_code
        access.save()
        
        return render(request, 'receptions-videomeasuring.html', {'access_id': access_id })
        

class RecordVideoView(APIView):
    """
    Args:
        APIView ([type]): [description]
    """
    
    parser_classes = (MultiPartParser,)

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
        
        # Prepare results
        p_measure_result = PatientMeasureResult()
        p_measure_result.patient_video = patient_video
        p_measure_result.save()
        #Make the measure
        video_path = os.path.join(settings.MEDIA_ROOT, video)
        config_path = os.path.join(settings.CORE_DIR, "config.json")
        config = load_config(config_path)
        measurement_id = asyncio.run(make_measure(config=config, config_path=config_path, video_path=video_path))
        
        return Response({'patient_video_id': patient_video.pk, 'measurement_id': measurement_id }, status=status.HTTP_200_OK)
    
class PatientResults(APIView):
    """
    Args:
        ApiView ([type]): [description]
    """
    
    def post(self, request, *args, **kwargs):
        
        patient_video_id = kwargs.get('patient_video_id')#TODO FIX
        return render(request,'receptions-results.html', {'patient_video_id': ''})
