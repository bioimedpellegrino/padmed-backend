
import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render,redirect
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from crispy_forms.utils import render_crispy_form
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
        
        now = timezone.localtime()
        one_hour_ago = now - relativedelta(hours=1)

        cards = GetStoricoData.get_storico_cards(one_hour_ago,now)

        units = {}
        units["temperature"] = "°C"
        units["pressure"] = "mmHg"
        units["heartrate"] = "bpm"
                
        items = TriageAccess.ordered_items()
        max_waiting_time = get_max_waiting_time()
        max_waiting = max_waiting_time.hours*60 + max_waiting_time.minutes
        for item in items:
            item_waiting_time = item.waiting_time
            item.waiting_cache = min(100*(item_waiting_time.days*24*60 + item_waiting_time.hours*60 + item_waiting_time.minutes)/max_waiting,100)
            item.waiting_fmt_cache = "%sh:%smin"%(item_waiting_time.days*24+item_waiting_time.hours,item_waiting_time.minutes)
            item.waiting_range_cache = min(int(item.waiting_cache/33.3),3)
            item.waiting_minutes_cache = item_waiting_time.days*24*60 + item_waiting_time.hours*60 + item_waiting_time.minutes
            
            item.hresults = None
            video = item.patientvideo_set.last()
            if video:
                measure = video.patientmeasureresult_set.last()
                if measure:
                    item.hresults = measure.get_hresult
                    
        return render(request, self.template_name, {
            "cards":cards,
            "items":items,
            "units":units,
            })

class StoricoView(APIView):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'storico.html'
    
    def get(self, request, *args, **kwargs):
        from .utils import get_max_waiting_time
        from .forms import DateRangeForm
        
        now = timezone.localtime() 
        one_day_ago = now - relativedelta(days=1)
        form = DateRangeForm(
            initial={   ## TODO: doesn't work
                "start":one_day_ago.date(),
                "end":now.date(),
                }
        )
        cards = GetStoricoData.get_storico_advanced_cards(one_day_ago,now)
        
        
                    
        return render(request, self.template_name, {
            "cards":cards,
            "form":form,
            })
        
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

class GetStoricoData(APIView):
    
    def post(self, request, *args, **kwargs):
        from .forms import DateRangeForm
        
        form = DateRangeForm(
            request.POST or None
        )
        
        ## Here it will need a timezone conversion https://stackoverflow.com/questions/18622007/runtimewarning-datetimefield-received-a-naive-datetime
        form = DateRangeForm(request.POST or None)
        
        if form.is_valid():
            # You could actually save through AJAX and return a success code here
            cards = self.get_storico_advanced_cards(form.cleaned_data["start"],form.cleaned_data["end"])
            
            return JsonResponse({'success': True,"cards":cards})
        else:
            ctx = {}
            ctx.update(csrf(request))
            form_html = render_crispy_form(form, context=ctx)
            
            return JsonResponse({'success': False, 'form_html': form_html})
        
    @classmethod
    def get_storico_cards(cls,start:datetime.datetime,end:datetime.datetime)->dict():
        
        diff_period = end - start
        diff_start = start - diff_period
        diff_end = start
        
        cards = dict()
        
        cards["gialli"] = dict()
        cards["verdi"] = dict()
        cards["bianchi"] = dict()
        cards["personale"] = dict()
        
        value = 0 #TriageAccess.whites(exit_date__isnull=True).count() #TODO
        diff = value - 0 #TriageAccess.whites(exit_date__gte=start,exit_date__lt=end).count()
        positive_trend = diff >= 0
        cards["personale"] = {
            "value" : "?",
            "diff": diff,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.yellows(access_date__gte=start,access_date__lte=end).count()
        diff = value - TriageAccess.yellows(access_date__gte=diff_start,access_date__lt=diff_end).count()
        positive_trend = diff >= 0
        cards["gialli"] = {
            "value" : value,
            "diff": diff,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.greens(access_date__gte=start,access_date__lte=end).count()
        diff = value - TriageAccess.greens(access_date__gte=diff_start,access_date__lt=diff_end).count()
        positive_trend = diff >= 0
        cards["verdi"] = {
            "value" : value,
            "diff": diff,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.whites(access_date__gte=start,access_date__lte=end).count()
        diff = value - TriageAccess.whites(access_date__gte=diff_start,access_date__lt=diff_end).count()
        positive_trend = diff >= 0
        cards["bianchi"] = {
            "value" : value,
            "diff": diff,
            "positive_trend" : positive_trend,
        }
        
        return cards

    @classmethod
    def get_storico_advanced_cards(cls,start:datetime.datetime,end:datetime.datetime)->dict():
        
        def filter_for_exit_interval(value,diff,from_hours=None,to_hours=None):
            from datetime import timedelta
            from django.db.models import F
            filter_dict = {}
            if from_hours:
                filter_dict["exit_date__gte"] = F("access_date")+timedelta(hours=from_hours)
            if to_hours:
                filter_dict["exit_date__lt"] = F("access_date")+timedelta(hours=to_hours)
            
            value = value.filter(**filter_dict)
            diff = diff.filter(**filter_dict)
            return value, diff
        
        diff_period = end - start
        diff_start = start - diff_period
        diff_end = start
        
        cards = dict()
        
        name_methods = [
            ("gialli","yellows"),
            ("verdi","greens"),
            ("bianchi","whites"),
        ]

        for name,method_name in name_methods:
            method = getattr(TriageAccess,method_name)
            
            value = method(access_date__gte=start,access_date__lte=end)
            diff = method(access_date__gte=diff_start,access_date__lt=diff_end)
            
            
            value_1,diff_1 = filter_for_exit_interval(value,diff,to_hours=2)
            value_2,diff_2 = filter_for_exit_interval(value,diff,from_hours=2,to_hours=4)
            value_3,diff_3 = filter_for_exit_interval(value,diff,from_hours=4)
            
            cards[name] = {
                "value" : value.count(),
                "diff" : value.count() - diff.count(),
                "trend" : value.count() - diff.count() >= 0,
                
                "value_1": value_1.count(),
                "diff_1": value_1.count() - diff_1.count(),
                "trend_1" : value_1.count() - diff_1.count() >= 0,
                "value_1_description" : "Meno di 2h",
                
                "value_2": value_2.count(),
                "diff_2": value_2.count() - diff_2.count(),
                "trend_2" : value_2.count() - diff_2.count() >= 0,
                "value_2_description" : "Tra 2h e 4h",
                
                "value_3": value_3.count(),
                "diff_3": value_3.count() - diff_3.count(),
                "trend_3" : value_3.count() - diff_3.count() >= 0,
                "value_3_description" : "Più di 4h",
            }
        
        return cards
    
