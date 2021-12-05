
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
        one_day_ago = now - relativedelta(days=30)
        form = DateRangeForm(
            {   ## TODO: doesn't work
            "start":one_day_ago.date().isoformat(),
            "start_cache":one_day_ago.date().isoformat(),
            "end":now.date().isoformat(),
            "end_cache":now.date().isoformat(),
            }
        )
        cards = GetStoricoData.get_storico_advanced_cards(one_day_ago,now)
        big_graph = GetStoricoData.get_storico_big_graph(one_day_ago,now)
                    
        return render(request, self.template_name, {
            "cards":cards,
            "form":form,
            "big_graph":big_graph,
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
        
        ## Here it will need a timezone conversion https://stackoverflow.com/questions/18622007/runtimewarning-datetimefield-received-a-naive-datetime
        form = DateRangeForm(request.POST or None)
        
        if form.is_valid():
            # You could actually save through AJAX and return a success code here
            cards = self.get_storico_advanced_cards(
                form.cleaned_data["start"],
                form.cleaned_data["end"]
                )
            big_graph = self.get_storico_big_graph(
                form.cleaned_data["start"],
                form.cleaned_data["end"],
                code = form.cleaned_data["code"],
                from_hours = form.cleaned_data["from_hours"],
                to_hours = form.cleaned_data["to_hours"],
                )
            return JsonResponse({
                'success': True,
                "cards":cards,
                "big_graph":big_graph,
                })
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
                
        last_period = end - start
        last_start = start - last_period
        last_end = start
        
        cards = dict()
        
        name_methods = [
            ("gialli","yellows"),
            ("verdi","greens"),
            ("bianchi","whites"),
        ]
        sign_format = {True:"+",False:""}
        class_format = {True:"text-warning",False:"text-success"}
        for name,method_name in name_methods:
            method = getattr(TriageAccess,method_name)
            
            value = method(access_date__gte=start,access_date__lte=end)
            last = method(access_date__gte=last_start,access_date__lt=last_end)
            diff = value.count() - last.count()
            
            value_1,last_1 = TriageAccess.filter_for_exit_interval(value,last,to_hours=2)
            diff_1 = value_1.count() - last_1.count()
            value_2,last_2 = TriageAccess.filter_for_exit_interval(value,last,from_hours=2,to_hours=4)
            diff_2 = value_2.count() - last_2.count()
            value_3,last_3 = TriageAccess.filter_for_exit_interval(value,last,from_hours=4)
            diff_3 = value_3.count() - last_3.count()
            
            cards[name] = {
                "value" : value.count(),
                "diff" : diff,
                "diff_formatted" : "("+sign_format[diff>=0]+str(diff)+")",
                "diff_class" : class_format[diff>=0],
                
                "value_1": value_1.count(),
                "diff_1": diff_1,
                "diff_1_formatted" : "("+sign_format[diff_1>=0]+str(diff_1)+")",
                "diff_1_class" : class_format[diff_1>=0],
                "value_1_description" : "Meno di 2h",
                
                "value_2": value_2.count(),
                "diff_2": diff_2,
                "diff_2_formatted" : "("+sign_format[diff_2>=0]+str(diff_2)+")",
                "diff_2_class" : class_format[diff_2>=0],
                "value_2_description" : "Tra 2h e 4h",
                
                "value_3": value_3.count(),
                "diff_3": diff_3,
                "diff_3_formatted" : "("+sign_format[diff_3>=0]+str(diff_3)+")",
                "diff_3_class" : class_format[diff_3>=0],
                "value_3_description" : "Più di 4h",
            }
        
        return cards
    
    @classmethod
    def get_storico_big_graph(cls,start:datetime.date,end:datetime.date,code=None,from_hours=None,to_hours=None)->dict():
        import json
        from .utils import timesteps_builder
        ## See https://www.chartjs.org/docs/latest/, 
        # https://www.chartjs.org/docs/latest/developers/updates.html, 
        # https://demos.creative-tim.com/argon-dashboard-pro-react/?_ga=2.191324073.2076643225.1638138645-576346499.1636196270#/documentation/charts
        
        print("")
        print("start",start)
        print("end",end)
        print("code",code)
        print("from_hours",from_hours)
        print("to_hours",to_hours)
        print("")
        
        name_methods = {
            "yellow":"yellows",
            "green":"greens",
            "white":"whites",
            None:"filter",
        }
        method = getattr(TriageAccess,name_methods[code])
        
        timesteps_months = timesteps_builder(start,end,"m")
        timesteps_weeks = timesteps_builder(start,end,"w")
        timesteps_days = timesteps_builder(start,end,"d")
        
        big_graph = {}
        
        ## MESI ##
        
        labels = []
        datas = []
        for i in range(len(timesteps_months)-1):
            start_date = timesteps_months[i]
            end_date = timesteps_months[i+1]
            ## Build label
            labels.append(start_date.strftime("%B")[:3])
            if start_date.month == 1:
                labels[-1] += " %s"%start_date.year
            ## Build data
            data = method(access_date__gte=start_date,access_date__lte=end_date)
            data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
            datas.append(data.count())
        print(labels)
        
        big_graph["months_data"] = {
            "data":{
                "labels":labels,
                "datasets":[
                        {
                            "label":"",
                            "data":datas
                        }
                    ]
                },
            }
        
        ## SETTIMANE ##
        
        labels = []
        datas = []
        for i in range(len(timesteps_months)-1):
            start_date = timesteps_months[i]
            end_date = timesteps_months[i+1]
            ## Build label
            labels.append(start_date.strftime("%B")[:3])
            if start_date.month == 1:
                labels[-1] += " %s"%start_date.year
            ## Build data
            data = method(access_date__gte=start_date,access_date__lte=end_date)
            data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
            datas.append(data.count())
            
        big_graph["weeks_data"] = {
            "data":{
                "labels":labels,
                "datasets":[
                        {
                            "label":"",
                            "data":datas
                        }
                    ]
                },
            }
        
        ## GIORNI ##
        
        big_graph["days_data"] = {
            "data":{
                "labels":labels,
                "datasets":[
                        {
                            "label":"",
                            "data":datas
                        }
                    ]
                },
            }
        
        return big_graph