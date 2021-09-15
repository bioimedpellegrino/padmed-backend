from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from codicefiscale import codicefiscale
import asyncio

from dfxapi.api import register_device #async
class DecodeFiscalCodeView(APIView):
    
    def post(self, request, *args, **kwargs):
        """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
        """
        return Response(
            codicefiscale.decode(request.data['fiscal_code']), 
            status=status.HTTP_200_OK)
        

class TestDFXApiView(APIView):
    
    def get(self, request, *args, **kwargs):
        """[summary]

        Args:
            request ([type]): [description]
        """
        response = asyncio.run(register_device())
        
        return Response(response, status=status.HTTP_200_OK)