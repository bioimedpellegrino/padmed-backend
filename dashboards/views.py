
import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from triage.models import *

class LiveView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    
    template_name = 'live_dash.html'
    
    def get(self, request, *args, **kwargs):
        from .utils import get_max_waiting_time
        
        now = timezone.now()
        one_hour_ago = now - relativedelta(hours=1)

        cards = dict()
        cards["gialli"] = dict()
        cards["verdi"] = dict()
        cards["bianchi"] = dict()
        cards["personale"] = dict()

        value = TriageAccess.yellows(exit_date__isnull=True).count()
        diff1h = -1 * TriageAccess.yellows(exit_date__gte=one_hour_ago,exit_date__lt=now).count()
        positive_trend = diff1h >= 0
        cards["gialli"] = {
            "value" : value,
            "diff1h": diff1h,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.greens(exit_date__isnull=True).count()
        diff1h = -1 * TriageAccess.greens(exit_date__gte=one_hour_ago,exit_date__lt=now).count()
        positive_trend = diff1h >= 0
        cards["verdi"] = {
            "value" : value,
            "diff1h": diff1h,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.whites(exit_date__isnull=True).count()
        diff1h = -1 * TriageAccess.whites(exit_date__gte=one_hour_ago,exit_date__lt=now).count()
        positive_trend = diff1h >= 0
        cards["bianchi"] = {
            "value" : value,
            "diff1h": diff1h,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.whites(exit_date__isnull=True).count()
        diff1h = -1 * TriageAccess.whites(exit_date__gte=one_hour_ago,exit_date__lt=now).count()
        positive_trend = diff1h >= 0
        cards["personale"] = {
            "value" : "?",
            "diff1h": diff1h,
            "positive_trend" : positive_trend,
        }

        items = TriageAccess.ordered_items()
        max_waiting_time = get_max_waiting_time()
        max_waiting = max_waiting_time.hours*60 + max_waiting_time.minutes
        for item in items:
            item_waiting_time = item.waiting_time
            item.waiting_cache = min(100*(item_waiting_time.days*24*60 + item_waiting_time.hours*60 + item_waiting_time.minutes)/max_waiting,100)
            item.waiting_fmt_cache = "%sh:%smin"%(item_waiting_time.hours,item_waiting_time.minutes)
            item.waiting_range_cache = min(int(item.waiting_cache/33.3),3)
        return render(request, self.template_name, {
            "cards":cards,
            "items":items,
            })

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
    
