from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from codicefiscale import codicefiscale
import asyncio

from dfxapi.api import register_device #async
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
        
        return render(request, self.template_name)