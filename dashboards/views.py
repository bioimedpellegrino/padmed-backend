
import datetime
from dateutil.relativedelta import relativedelta

from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.views.generic import View
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from crispy_forms.utils import render_crispy_form
from rest_framework.views import APIView

from triage.models import *
from app.models import AppUser

# from django.http import Http404

class LiveView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    
    template_name = 'live_dash.html'
    
    def get(self, request, *args, **kwargs):
        from .utils import get_max_waiting_time
        user = AppUser.get_or_create_from_parent(request.user)
        if user.hospital_logged is None:
            current_url = request.resolver_match.url_name
            messages.add_message(request, messages.WARNING, _('Seleziona un ospedale per usare le dashboard'))
            return HttpResponseRedirect('%s?next=%s' % (reverse('hospitals'), current_url))
        
        # totems = user.hospital_logged.totems() #TODO
        
        now = timezone.localtime()
        one_hour_ago = now - relativedelta(hours=1)

        cards = GetStoricoData.get_storico_cards(one_hour_ago,now)

        units = {}
        units["temperature"] = "°C"
        units["pressure"] = "mmHg"
        units["heartrate"] = "bpm"
                
        items = TriageAccess.ordered_items(exit_date__isnull=True)
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

class StoricoView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'storico.html'
    
    def get(self, request, *args, **kwargs):
        from .utils import get_max_waiting_time
        from .forms import DateRangeForm
        
        user = AppUser.get_or_create_from_parent(request.user)
        if user.hospital_logged is None:
            current_url = request.resolver_match.url_name
            messages.add_message(request, messages.WARNING, _('Seleziona un ospedale per continuare con le dashboard'))
            return HttpResponseRedirect('%s?next=%s' % (reverse('hospitals'), current_url))
        
        # totems = user.hospital_logged.totems() #TODO
        
        now = timezone.localtime() 
        one_day_ago = now - relativedelta(days=250)
        form = DateRangeForm(
            { 
                "start":one_day_ago.date().isoformat(),
                "start_cache":one_day_ago.date().isoformat(),
                "end":now.date().isoformat(),
                "end_cache":now.date().isoformat(),
            }
        )
        cards = GetStoricoData.get_storico_advanced_cards(one_day_ago,now)
        big_graph = GetStoricoData.get_storico_big_graph(one_day_ago,now)
        bar_graph = GetStoricoData.get_storico_bar_graph(one_day_ago,now)
        storico_table = GetStoricoData.get_storico_table(one_day_ago,now)
        return render(request, self.template_name, {
            "cards":cards,
            "form":form,
            "big_graph":big_graph,
            "bar_graph":bar_graph,
            "storico_table":storico_table,
            })

class UserProfileView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'profile.html'
    
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        from .forms import AppUserEditForm
        from app.models import AppUser
        from triage.models import Hospital
        #### Objects from post ####
        form = kwargs.get("form",None)
        has_error = kwargs.get("has_error",False)
        ###########################
        
        user = AppUser.get_or_create_from_parent(request.user)
        if not form:
            form = AppUserEditForm(
                instance = user,
            )
        return render(request, self.template_name, {
            "form":form,
            "has_error":has_error,
        })
        
    def post(self, request, *args, **kwargs):
        from .forms import AppUserEditForm
        from django.contrib import messages
        from app.models import AppUser
        user = AppUser.get_or_create_from_parent(request.user)
        form = AppUserEditForm(
            request.POST or None,
            instance = user,
        )
        if form.is_valid():
            modified_user = form.save()
            messages.add_message(request, messages.SUCCESS, _('Modifiche salvate correttamente.'))
            return HttpResponseRedirect(reverse('user_profile'))
        else:
            kwargs["form"] = form
            kwargs["has_error"] = True
            return self.GET_render(request, *args, **kwargs)

class HospitalsView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'hospitals.html'
    
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        from .forms import HospitalSelectForm
        from triage.models import Hospital
        #### Objects from post ####
        form = kwargs.get("form",None)
        has_error = kwargs.get("has_error",False)
        ###########################
        
        user = AppUser.get_or_create_from_parent(request.user)
        hospitals = Hospital.filter_for_request("view",request)
        editable_hospitals = Hospital.filter_for_request("change",request)
        logged_hospital = user.hospital_logged
        if not form:
            form = HospitalSelectForm(
                queryset = hospitals,
                initial={"hospital":logged_hospital}
            )
        return render(request, self.template_name, {
            "form":form,
            "has_error":has_error,
            "hospitals":hospitals,
            "editable_hospitals":editable_hospitals,
            "logged_hospital":logged_hospital,
        })
        
    def post(self, request, *args, **kwargs):
        from .forms import HospitalSelectForm
        user = AppUser.get_or_create_from_parent(request.user)
        next_page = request.GET.get("next","hospitals")
        
        form = HospitalSelectForm(
            request.POST or None,
        )
        if form.is_valid():
            user.hospital_logged = form.cleaned_data["hospital"]
            user.save()
            messages.add_message(request, messages.SUCCESS, _('Profilo attivato: %s.'%(user.logged_profile)))
            return HttpResponseRedirect(reverse(next_page))
        else:
            kwargs["form"] = form
            kwargs["has_error"] = True
            return self.GET_render(request, *args, **kwargs)

class HospitalEditView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'hospital_edit.html'
    
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        from .forms import HospitalEditForm
        from triage.models import Hospital
        #### Objects from post ####
        form = kwargs.get("form",None)
        has_error = kwargs.get("has_error",False)
        ###########################
    
        id = kwargs.get("id", None)
        if id is not None:
            obj = get_object_or_404(Hospital,pk=id)
            permission = obj.has_change_permission(request)
        else:
            obj = None
            permission = Hospital.has_global_add_permission(request)
        if permission:
            if not form:
                form = HospitalEditForm(
                    instance = obj,
                )
            return render(request, self.template_name, {
                "form":form,
                "has_error":has_error,
            })
        else:
            raise PermissionDenied
        
    def post(self, request, *args, **kwargs):
        from .forms import HospitalEditForm
        from django.contrib import messages
        from app.models import AppUser
        id = kwargs.get("id", None)
        if id is not None:
            obj = get_object_or_404(Hospital,pk=id)
            permission = obj.has_change_permission(request)
        else:
            obj = None
            permission = Hospital.has_global_add_permission(request)
        if permission:
            form = HospitalEditForm(
                request.POST or None,
                request.FILES or None,
                instance = obj,
            )
            if form.is_valid():
                obj = form.save()
                messages.add_message(request, messages.SUCCESS, _('Ospedale "%s" salvato con successo!'%(obj)))
                return HttpResponseRedirect(reverse('hospitals'))
            else:
                kwargs["form"] = form
                kwargs["has_error"] = True
                return self.GET_render(request, *args, **kwargs)
        else:
            raise PermissionDenied

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
            bar_graph = self.get_storico_bar_graph(
                form.cleaned_data["start"],
                form.cleaned_data["end"],
                code = form.cleaned_data["code"],
                from_hours = form.cleaned_data["from_hours"],
                to_hours = form.cleaned_data["to_hours"],
                )
            storico_table = self.get_storico_table(
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
                "bar_graph":bar_graph,
                "storico_table":storico_table,
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
        last_year = None
        for i in range(len(timesteps_weeks)-1):
            start_date = timesteps_weeks[i]
            end_date = timesteps_weeks[i+1]
            ## Build label
            labels.append(start_date.strftime("%d/%m"))
            if start_date.year != last_year:
                labels[-1] += start_date.strftime("/%Y")
                last_year = start_date.year
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
        labels = []
        datas = [] 
        last_year = None
        for i in range(len(timesteps_days)-1):
            start_date = timesteps_days[i]
            end_date = timesteps_days[i+1]
            ## Build label
            labels.append(start_date.strftime("%d/%m"))
            if start_date.year != last_year:
                labels[-1] += start_date.strftime("/%Y")
                last_year = start_date.year
            ## Build data
            data = method(access_date__gte=start_date,access_date__lte=end_date)
            data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
            datas.append(data.count())
        
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
    
    @classmethod
    def get_storico_bar_graph(cls,start:datetime.date,end:datetime.date,code=None,from_hours=None,to_hours=None):
        from django.db.models import Count
        
        name_methods = {
            "yellow":"yellows",
            "green":"greens",
            "white":"whites",
            None:"filter",
        }
        method = getattr(TriageAccess,name_methods[code])
        
        data = method(access_date__gte=start,access_date__lte=end)
        data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
        data = data.values('access_reason__reason').annotate(total=Count('access_reason')).order_by("access_reason__reason")
        
        labels = [reason["access_reason__reason"] for reason in data]
        datas = [reason["total"] for reason in data]
        
        data ={
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
        return data
    
    @classmethod
    def get_storico_table(cls,start:datetime.date,end:datetime.date,code=None,from_hours=None,to_hours=None):
        from django.template.loader import render_to_string
        import re
        
        name_methods = {
            "yellow":"yellows",
            "green":"greens",
            "white":"whites",
            None:"filter",
        }
        method = getattr(TriageAccess,name_methods[code])

        units = {}
        units["temperature"] = "°C"
        units["pressure"] = "mmHg"
        units["heartrate"] = "bpm"
                
        data = method(access_date__gte=start,access_date__lte=end)
        data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
        data = data.order_by("access_date")
        for item in data:
            item.access_date_cache = item.access_date.strftime("%d/%m/%Y %H:%M")
            item.access_date_order_cache = int(item.access_date.strftime("%Y%m%d%H%M"))
            item.hresults = None
            video = item.patientvideo_set.last()
            if video:
                measure = video.patientmeasureresult_set.last()
                if measure:
                    item.hresults = measure.get_hresult
        
        table = render_to_string("includes/storico_table.html",{
            "items":data,
            "units":units,            
        })
        table = re.sub(r'\s*\n\s*', ' ', table).strip()
        return str(table)