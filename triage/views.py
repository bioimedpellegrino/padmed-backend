from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.http import HttpResponseRedirect, JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from codicefiscale import codicefiscale
from app.decorators import totem_login_required
from deepaffex.api import register_device, login, get_studies_by_id, get_studies_list, select_study, get_measurements_list, get_measurement, retrieve_sdk_config, make_measure #async
from deepaffex.utils import save_config, load_config
import asyncio, datetime, os, json, time, traceback

from app.models import AppUser
from logger.utils import add_log
from .forms import PatientForm
from .models import Hospital, Patient, TriageCode, TriageAccessReason, TriageAccess, \
    PatientVideo, PatientMeasureResult, MeasureLogger, Totem
from .utils import generate_video_measure, unpack_result_deepaffex, print_command_measure

class RedirectView(View):
    def get(self, request, *args, **kwargs):
        url_name = kwargs["url_name"]
        url_kwargs = kwargs.get("url_kwargs",{})
        return redirect(reverse(url_name,kwargs=url_kwargs))
    
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
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        
        form = PatientForm()
        user = AppUser.get_or_create_from_parent(request.user)
        use_card_reader = settings.USE_CARD_READER
        return render(request, self.TEMPLATE_NAME, {'form': form, 'user': user,'use_card_reader':use_card_reader})
    
    @method_decorator(totem_login_required(login_url="/login/"))
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
            patient.birth_date = fiscal_code_decoded["birthdate"]
            patient.birth_place_city = fiscal_code_decoded["birthplace"]
            patient.gender = fiscal_code_decoded["sex"]
            patient.save()
            
            declared_anag = patient.declared_anag
            already_compiled = False
            if declared_anag is not None:
                already_compiled = declared_anag.compiled
                print("already_compiled",already_compiled)
            if not already_compiled:
                patient.declared_anag = {
                    "birth_year":fiscal_code_decoded["birthdate"].year,
                    "gender":{"M":"male","F":"female"}[fiscal_code_decoded["sex"]],
                } 
            
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
            access.status_tracker.status = access.status_tracker.created
            access.save()
            
            if not already_compiled:
                return HttpResponseRedirect(reverse('access_anagrafica',kwargs={"access_id":access.id}))
            else:
                return HttpResponseRedirect(reverse('accessreason',kwargs={"access_id":access.id}))
        else:
            print("Errors",form.errors)
            # TODO
            form = PatientForm()
            return render(request, self.TEMPLATE_NAME, {'form': form, 'errors': 'Il codice fiscale inserito non è valido', 'user': user})

class AnagraficaView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    TEMPLATE_NAME = 'receptions-anagrafica.html'
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        from .forms import AnagraficaForm
        user = AppUser.get_or_create_from_parent(request.user)
        access_id = int(kwargs.get('access_id', None))
        access = get_object_or_404(TriageAccess,pk=access_id)
        patient = access.patient
        declared_anag = patient.declared_anag
        form = AnagraficaForm(instance=declared_anag)
        return render(request, self.TEMPLATE_NAME, {'form': form, 'user': user})
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        from .forms import AnagraficaForm
        user = AppUser.get_or_create_from_parent(request.user)
        totem = user.totem_logged
        if not totem:
            raise PermissionDenied("Solo gli utenti Totem sono abilitati all'inserimento dei dati. Effettura il login con un utente Totem o contattare l'assistenza.")
        hospital = totem.hospital
        
        if not hospital:
            raise PermissionDenied("Questo Totem non ha un hospedale associato. Associare un ospedale al Totem o contattare l'assistenza.")

        access_id = int(kwargs.get('access_id', None))
        access = get_object_or_404(TriageAccess,pk=access_id)
        patient = access.patient
        declared_anag = patient.declared_anag
        print("request.POST")
        print(request.POST)
        form = AnagraficaForm(request.POST,instance=declared_anag)
        
        if form.is_valid():
            declared_anag = form.save()
            return HttpResponseRedirect(reverse('accessreason',kwargs={"access_id":access.id}))
        else:
            print("Errors",form.errors)
            return render(request, self.TEMPLATE_NAME, {'form': form, 'has_error': True, 'user': user})
        
class ReceptionsReasonsView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    
    TEMPLATE_NAME = 'receptions-accessreason.html'
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        user = AppUser.get_or_create_from_parent(request.user)
        access_id = int(kwargs.get('access_id', None))
        access = get_object_or_404(TriageAccess,pk=access_id)
        
        reasons = TriageAccessReason.objects.filter(hospital=access.hospital).order_by('order') #TODO: filter by "enable" (to be defined)

        return render(request, self.TEMPLATE_NAME, {'access_id': access_id, 'reasons': reasons, 'user': user})
    
    @method_decorator(totem_login_required(login_url="/login/"))
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
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        user = AppUser.get_or_create_from_parent(request.user)
        access_id = kwargs.get('access_id', None)
        access = get_object_or_404(TriageAccess,pk=access_id)
        ROTATE_90_COUNTERCLOCKWISE = settings.ROTATE_90_COUNTERCLOCKWISE
        access.status_tracker.status = access.status_tracker.recording_video
        return render(request, self.TEMPLATE_NAME, {'access_id': access_id, 'user': user,"ROTATE_90_COUNTERCLOCKWISE":ROTATE_90_COUNTERCLOCKWISE})
    
    parser_classes = (MultiPartParser,)
    @method_decorator(totem_login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        try:
            video = request.FILES['video']
            access_id = kwargs.get('access_id')
            triage_access = TriageAccess.objects.get(pk=access_id)

            triage_access.status_tracker.status = triage_access.status_tracker.saving_video
            
            file_path = default_storage.save('tmp/' + "{}.webm".format(access_id), video)

            video = generate_video_measure(file_path, access_id)
            
            patient_video = PatientVideo()
            patient_video.triage_access = triage_access
            patient_video.video = video
            patient_video.save()
            #Make the measure
            anagrafica = triage_access.patient.declared_anag.to_anag()
            video_path = os.path.join(settings.MEDIA_ROOT, video)
            triage_access.status_tracker.status = triage_access.status_tracker.loading_configurations
            config_path = os.path.join(settings.CORE_DIR, "config.json")
            config = load_config(config_path)
            triage_access.status_tracker.status = triage_access.status_tracker.data_preelaborations
            measurement_id, logs = asyncio.run(make_measure(config=config, config_path=config_path, video_path=video_path, demographics=anagrafica, start_time=settings.START_TIME, end_time=settings.END_TIME))
            # Logger
            # triage_access.status_tracker.status = triage_access.status_tracker.saving_logs
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
            # triage_access.status_tracker.status = triage_access.status_tracker.receiving_results
            result = asyncio.run(get_measurement(config=config, measurement_id=measurement_id))
            p_measure_result.result = result
            p_measure_result.save()
            triage_access.status_tracker.status = triage_access.status_tracker.unpack_results
            try:
                p_measure_result.measure_short = unpack_result_deepaffex(result)
            except KeyError as ke:
                if str(ke.args[0])=="Results":
                    return Response({
                        'p_measure_result': p_measure_result.pk, 
                        'success':False, 
                        'error': 'Qualità video troppo bassa.' 
                        }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'p_measure_result': p_measure_result.pk, 
                        'success':False, 
                        'error': 'Chiave mancante: %s'%str(ke) 
                        }, status=status.HTTP_200_OK)                    
            
            p_measure_result.save()
            triage_access.status_tracker.status = triage_access.status_tracker.printing_results
            
            return Response({
                'p_measure_result': p_measure_result.pk, 
                'success':True, 
                'error': None }, status=status.HTTP_200_OK)
        except Exception as e:
            message= "An exception occurred during video elaboration in RecordVideoView"
            traceback.print_exc()
            add_log(level=5, message=1, exception=traceback.format_exc(), custom_message=message, request=request)
            return Response({
                'p_measure_result': p_measure_result.pk, 
                'success':False, 
                'error': "Errore generico di tipo %s: %s"%(e.__class__.__name__,str(e)) 
                }, status=status.HTTP_200_OK)
    
class PatientResults(APIView):
    """
    Args:
        ApiView ([type]): [description]
    """
    @method_decorator(totem_login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        patient_result = PatientMeasureResult.objects.get(pk=int(request.POST.get('p_measure_result')))
        measure = eval(patient_result.measure_short)
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')
        print_command = print_command_measure(measure, today_date)
        return render(request,'receptions-results.html', {'measure': measure, 'date': today_date, 'user': user, 'print_command': print_command, 'show_arrow': True})
    
class PatientResultsError(APIView):
    """
    Args:
        ApiView ([type]): [description]
    """
    @method_decorator(totem_login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        access_id = request.POST.get('access_id')
        error = request.POST.get('error')
        return render(request,'receptions-results.html', {'error': error, 'user': user,'access_id':access_id})

class TestNFC(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        print_command = '<BIG><BOLD><CENTER> PADMED <BR><CENTER>Esito misurazione<BR><CENTER>Data:2022-02-19<BR><BOLD>Misurazione:<BR><BOLD>Misurazione:<BR><LEFT><BOLD>General Wellness Score: 83.33 <BR><LEFT><BOLD>Vital Score: 3.5 <BR><LEFT><BOLD>Physiological Score: 4.0 <BR><LEFT><BOLD>Mental Score: 4.0 <BR><LEFT><BOLD>Physical Score: 4.33 <BR><LEFT><BOLD>Risks Score: 5.0 <BR><LEFT><BOLD>NuraLogix Mental Stress Index: 2.88 <BR><LEFT><BOLD>NuraLogix Mental Stress Index: 2.88 <BR><LEFT><BOLD>HR Variability (SDNN): 38.2 ms<BR><LEFT><BOLD>Heart Rate 140 (bpm): 58.13 bpm<BR><LEFT><BOLD>Heart Rate 140 (Hz): 0.97 Hz<BR><LEFT><BOLD>Beat-to-beat Interval: 1.03 <BR><LEFT><BOLD>Signal-to-Noise Ratio (SNR): 1.25 dB<BR><LEFT><BOLD>Facial Topographical Age: 36.0 yrs<BR><LEFT><BOLD>Gender: 1.0 M/F<BR><LEFT><BOLD>Height (cm): 166.98 cm<BR><LEFT><BOLD>Weight (kg): 88.04 kg<BR><LEFT><BOLD>Waist Circumference: 81.24 cm<BR><LEFT><BOLD>Body Shape Index: 7.81 <BR><LEFT><BOLD>Waist-to-height Ratio: 45.13 %<BR><LEFT><BOLD>Systolic Blood Pressure: 129.48 mmHg<BR><LEFT><BOLD>Diastolic Blood Pressure: 75.97 mmHg<BR><LEFT><BOLD>Pulse Pressure: 59.4 mmHg<BR><LEFT><BOLD>Mean Arterial Pressure: 93.81 mmHg<BR><LEFT><BOLD>Stroke Risk: 0.44 %<BR><LEFT><BOLD>Heart Attack Risk: 0.01 %<BR><LEFT><BOLD>Cardiovascular Disease Risk: 0.33 %<BR><LEFT><BOLD>Cardiac Workload: 3.9 dB<BR><LEFT><BOLD>Vascular Capacity: 1.55 seconds<BR><LEFT><BOLD>Breathing Rate (bpm): 10.95 bpm<BR><LEFT><BOLD>Breathing Rate (Hz): 0.18 Hz<BR><LEFT><BOLD>Irregular Heartbeats: 0.0 <BR><LEFT><BOLD>Calculated Body Mass Index: 21.6 kg/m²<BR><CUT>'
        return render(request,'testnfc.html', {'show_arrow': True, 'print_command': print_command})

class VideoSelecting(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):

        return render(request,'videoselecting.html')

class UserConditions(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        
        return render(request,'receptions-conditions.html', {'user': user}) # receptions-conditions.html
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        
        return HttpResponseRedirect(reverse('receptions'))
    
### AJAX GET VIEWS ###

class GetAccessStatusView(APIView):
    
    ACCESS_STATUS = {
        "created":"Accesso registrato",
        "recording_video":"Registrazione del video",
        "saving_video":"Salvataggio del video",
        "loading_configurations":"Caricamento configurazioni",
        "initializing_dfx":"Inizializzazione strumenti di analisi",
        "data_preelaborations":"Elaborazione del video",
        "saving_logs":"Salvataggio dei log",
        "receiving_results":"Ricezione risultati",
        "unpack_results":"Lettura risultati",
        "printing_results":"Stampa risultati",
    }
    
    @method_decorator(totem_login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        access_id = request.GET.get('access_id', None)
        access = get_object_or_404(TriageAccess,pk=access_id)
        status = access.status_tracker.status
        fe_status = self.ACCESS_STATUS[status]
        return JsonResponse({"status":fe_status})

    