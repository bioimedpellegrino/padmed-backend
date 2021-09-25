from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from codicefiscale import codicefiscale
import asyncio
from dfxapi.api import register_device #async

from .forms import PatientForm
from .models import Hospital, Patient, TriageCode, TriageAccessReason, TriageAccess

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
    template_name = 'receptions.html'
    
    def get(self, request, *args, **kwargs):
        
        form = PatientForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        
        form = PatientForm(request.POST)
        
        if form.is_valid():
            fiscal_code = str(form.cleaned_data['fiscal_code']).upper()
            fiscal_code_decoded = codicefiscale.decode(fiscal_code)
            patient, created = Patient.objects.get_or_create(fiscal_code=fiscal_code_decoded['code'])
            if created:
                patient.birth_date = fiscal_code_decoded['birthdate']
                patient.gender = fiscal_code_decoded['sex']
                patient.birth_place = fiscal_code_decoded['birthplace']['name']
                patient.save()
            
            access = PatientAccess
            return render(request, self.template_name, {'form': form})
        else:
            form = PatientForm()
            return render(request, self.template_name, {'form': form, 'errors': 'Il codice fiscale inserito non è valido'})