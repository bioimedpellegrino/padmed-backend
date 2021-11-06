from django.shortcuts import render
from rest_framework.views import APIView
from triage.models import *

class LiveView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'livetables.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})
    
