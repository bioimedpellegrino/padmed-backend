from django.shortcuts import render
from rest_framework.views import APIView
from triage.models import *

class LiveView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'live_dash.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})

class StoricoView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'index.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})
        
class IconsView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'icons.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})
        
class MapsView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'maps.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})

class UserProfileView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'profile.html'
    
    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, {})
    
