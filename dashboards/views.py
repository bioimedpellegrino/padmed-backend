
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
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from crispy_forms.utils import render_crispy_form
from rest_framework.views import APIView

from triage.models import *
from app.models import AppUser

# from django.http import Http404

class LiveView(View):
    
    template_name = 'live_dash.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        user = AppUser.get_or_create_from_parent(request.user)
        if user.dashboard_hospital is None:
            current_url = request.resolver_match.url_name
            messages.add_message(request, messages.WARNING, _('Seleziona un ospedale per usare le dashboard'))
            return HttpResponseRedirect('%s?next=%s' % (reverse('hospitals'), current_url))
        
        hospital = user.dashboard_hospital
        
        now = timezone.localtime()
        one_hour_ago = relativedelta(hours=1)

        cards = GetLiveData.get_live_cards(start=None,end=now,diff_period=one_hour_ago,hospital=hospital)
        live_table = GetLiveData.get_live_table(
            request,
            hospital
            )
                    
        return render(request, self.template_name, {
            "cards":cards,
            "live_table":live_table,
            })

class AccessView(View):
    template_name = 'access.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):        
        user = AppUser.get_or_create_from_parent(request.user)
        id = kwargs.get("id", None)
        access = get_object_or_404(TriageAccess,pk=id)
        hospital = access.hospital
        permission = hospital.has_view_permission(user=user) or user==access.patient.appuser
        if permission:
            pass
        else:
            raise PermissionDenied
                    
        return render(request, self.template_name, {
            "access":access,
            })
        
class StoricoView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'storico.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        from .forms import DateRangeForm
        
        user = AppUser.get_or_create_from_parent(request.user)
        if user.dashboard_hospital is None:
            current_url = request.resolver_match.url_name
            messages.add_message(request, messages.WARNING, _('Seleziona un ospedale per continuare con le dashboard'))
            return HttpResponseRedirect('%s?next=%s' % (reverse('hospitals'), current_url))
        
        hospital = user.dashboard_hospital
        
        now = timezone.localtime() 
        one_day_ago = now - relativedelta(days=30)
        form = DateRangeForm(
            { 
                "start":one_day_ago.date().isoformat(),
                # "start_cache":one_day_ago.date().isoformat(),
                "end":now.date().isoformat(),
                # "end_cache":now.date().isoformat(),
            }
        )
        cards = GetStoricoData.get_storico_advanced_cards(one_day_ago,now,hospital=hospital)
        big_graph = GetStoricoData.get_storico_big_graph(one_day_ago,now,hospital=hospital)
        bar_graph = GetStoricoData.get_storico_bar_graph(one_day_ago,now,hospital=hospital)
        storico_table = GetStoricoData.get_storico_table(request,one_day_ago,now,hospital=hospital)
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
    
    @method_decorator(login_required(login_url="/login/"))
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
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        from .forms import AppUserEditForm
        from django.contrib import messages
        from app.models import AppUser
        user = AppUser.get_or_create_from_parent(request.user)
        form = AppUserEditForm(
            request.POST or None,
            request.FILES or None,
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
    default_post_page = "hospitals"
    
    @method_decorator(login_required(login_url="/login/"))
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
        logged_hospital = user.dashboard_hospital
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
    
    @method_decorator(login_required(login_url="/login/"))
    def post(self, request, *args, **kwargs):
        from .forms import HospitalSelectForm
        user = AppUser.get_or_create_from_parent(request.user)
        next_page = request.GET.get("next",self.default_post_page)
        
        form = HospitalSelectForm(
            request.POST or None,
        )
        if form.is_valid():
            user.dashboard_hospital = form.cleaned_data["hospital"]
            user.save()
            if next_page==self.default_post_page:   # TODO: da levare. Il messaggio deve uscire sempre, solo che per come è strutturato adesso copre 
                                        # gli altri oggetti, quindi momentaneamente lo tolgo.
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
    
    @method_decorator(login_required(login_url="/login/"))
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
    
    @method_decorator(login_required(login_url="/login/"))
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

class PatientsView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'patients.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        from .forms import HospitalSelectForm
        from triage.models import Hospital
        
        user = AppUser.get_or_create_from_parent(request.user)
        if user.dashboard_hospital is None:
            current_url = request.resolver_match.url_name
            messages.add_message(request, messages.WARNING, _('Seleziona un ospedale per accedere alla sezione pazienti.'))
            return HttpResponseRedirect('%s?next=%s' % (reverse('patients'), current_url))
        
        hospital = user.dashboard_hospital
        
        permission = hospital.has_view_permission(user=user)
        if permission:
            patients = hospital.access_patient_set
            return render(request, self.template_name, {
                "patients":patients,
            })
        else:
            raise PermissionDenied

class PatientView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'patient.html'
    
    @method_decorator(login_required(login_url="/login/"))
    def get(self, request, *args, **kwargs):
        return self.GET_render(request,*args, **kwargs)
    
    def GET_render(self,request,*args, **kwargs):
        
        id = kwargs.get("id", None)
        user = AppUser.get_or_create_from_parent(request.user)
        if user.dashboard_hospital is None:
            current_url = request.resolver_match.url_name
            messages.add_message(request, messages.WARNING, _('Seleziona un ospedale per accedere alla sezione pazienti.'))
            return HttpResponseRedirect('%s?next=%s' % (reverse('patient',id=id), current_url))
        hospital = user.dashboard_hospital
        if id is not None:
            patient = get_object_or_404(Patient,pk=id)
            hospitals = Hospital.objects.filter(id__in=patient.accesses.all().values_list("hospital_id",flat=True))
            # permission = any([hospital.has_view_permission(user=user) for hospital in hospitals])
            permission = hospital in hospitals
        else:
            patient = None
            permission = True
        if permission:
            accesses = patient.accesses.filter(hospital=hospital).order_by("access_date")
            accesses_table = GetStoricoData.get_table(request,accesses)
            return render(request, self.template_name, {
                "patient":patient,
                "accesses_table":accesses_table,
            })
        else:
            raise PermissionDenied

class PatientEditView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'hospital_edit.html'
    
    @method_decorator(login_required(login_url="/login/"))
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
    
    @method_decorator(login_required(login_url="/login/"))
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

class TotemEditView(View):
    """[summary]

    Args:
        APIView ([type]): [description]
    """
    template_name = 'hospital_edit.html'
    
    @method_decorator(login_required(login_url="/login/"))
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
    
    @method_decorator(login_required(login_url="/login/"))
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

class GetLiveData():
        
    @classmethod
    def get_live_cards(cls,start:datetime.datetime=None,end:datetime.datetime=None,diff_period:datetime.datetime=None,hospital:Hospital=None)->dict():
        from django.db.models import Q
        if end is not None:
            filter = Q(exit_date__isnull=True)|Q(exit_date__gt=end)
            diff_filter = Q(exit_date__isnull=True)|Q(exit_date__gt=end)
        else:
            filter = Q(exit_date__isnull=True)
            diff_filter = Q(exit_date__isnull=True)
            
        if start is not None:
            filter = filter & Q(access_date__gte=start)
            diff_filter = diff_filter & Q(access_date__gte=start - diff_period)
        if end is not None:
            filter = filter & Q(access_date__lte = end)
            diff_filter = diff_filter & Q(access_date__lte=end - diff_period)
        if hospital is not None:
            filter = filter & Q(hospital=hospital)
            diff_filter = diff_filter & Q(hospital=hospital)
        cards = dict()
        
        cards["gialli"] = dict()
        cards["verdi"] = dict()
        cards["bianchi"] = dict()
        # cards["personale"] = dict()
        
        # value = 0 #TriageAccess.whites(exit_date__isnull=True).count() #TODO
        # diff = value - 0 #TriageAccess.whites(exit_date__gte=start,exit_date__lt=end).count()
        # positive_trend = diff >= 0
        # cards["personale"] = {
        #     "value" : "?",
        #     "diff": diff,
        #     "positive_trend" : positive_trend,
        # }
        
        value = TriageAccess.yellows(filter).count()
        diff = value - TriageAccess.yellows(diff_filter).count()
        positive_trend = diff >= 0
        cards["gialli"] = {
            "value" : value,
            "diff": diff,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.greens(filter).count()
        diff = value - TriageAccess.greens(diff_filter).count()
        positive_trend = diff >= 0
        cards["verdi"] = {
            "value" : value,
            "diff": diff,
            "positive_trend" : positive_trend,
        }

        value = TriageAccess.whites(filter).count()
        diff = value - TriageAccess.whites(diff_filter).count()
        positive_trend = diff >= 0
        cards["bianchi"] = {
            "value" : value,
            "diff": diff,
            "positive_trend" : positive_trend,
        }
        
        return cards

    @classmethod
    def get_live_table(cls,request,hospital:Hospital):
        data = TriageAccess.ordered_items(exit_date__isnull=True,hospital=hospital)
        table = cls.get_table(request,data)
        return table
    
    @classmethod
    def get_table(cls,request,data):
        import re
        from django.template.loader import render_to_string
        from .utils import get_max_waiting_time
        
        units = {}
        units["temperature"] = "°C"
        units["pressure"] = "mmHg"
        units["heartrate"] = "bpm"
        
        max_waiting_time = get_max_waiting_time()
        max_waiting = max_waiting_time.hours*60 + max_waiting_time.minutes
        for item in data:
            item_waiting_time = item.waiting_time
            item.waiting_cache = min(100*(item_waiting_time.days*24*60 + item_waiting_time.hours*60 + item_waiting_time.minutes)/max_waiting,100)
            item.waiting_fmt_cache = "%sh:%smin"%(item_waiting_time.days*24+item_waiting_time.hours,item_waiting_time.minutes)
            item.waiting_range_cache = min(int(item.waiting_cache/33.3),3)
            item.waiting_minutes_cache = item_waiting_time.days*24*60 + item_waiting_time.hours*60 + item_waiting_time.minutes
            
            item.hresults = item.last_hresult
        
        table = render_to_string("includes/live_table.html",{
            "items":data,
            "units":units,            
        }, request=request)
        table = re.sub(r'\s*\n\s*', ' ', table).strip()
        return str(table)
        
class GetStoricoData(APIView):
    
    def post(self, request, *args, **kwargs):
        from .forms import DateRangeForm
        
        user = AppUser.get_or_create_from_parent(request.user)        
        hospital = user.dashboard_hospital
        
        ## Here it will need a timezone conversion https://stackoverflow.com/questions/18622007/runtimewarning-datetimefield-received-a-naive-datetime
        form = DateRangeForm(request.POST or None)
        
        if form.is_valid():
            # You could actually save through AJAX and return a success code here
            cards = self.get_storico_advanced_cards(
                form.cleaned_data["start"],
                form.cleaned_data["end"],
                code = form.cleaned_data["code"],
                from_hours = form.cleaned_data["from_hours"],
                to_hours = form.cleaned_data["to_hours"],
                hospital=hospital,
                )
            big_graph = self.get_storico_big_graph(
                form.cleaned_data["start"],
                form.cleaned_data["end"],
                code = form.cleaned_data["code"],
                from_hours = form.cleaned_data["from_hours"],
                to_hours = form.cleaned_data["to_hours"],
                hospital=hospital,
                )
            bar_graph = self.get_storico_bar_graph(
                form.cleaned_data["start"],
                form.cleaned_data["end"],
                code = form.cleaned_data["code"],
                from_hours = form.cleaned_data["from_hours"],
                to_hours = form.cleaned_data["to_hours"],
                hospital=hospital,
                )
            storico_table = self.get_storico_table(
                request,
                form.cleaned_data["start"],
                form.cleaned_data["end"],
                code = form.cleaned_data["code"],
                from_hours = form.cleaned_data["from_hours"],
                to_hours = form.cleaned_data["to_hours"],
                hospital=hospital,
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
    def get_storico_advanced_cards(cls,start:datetime.datetime,end:datetime.datetime,code=None,from_hours=None,to_hours=None,hospital:Hospital=None)->dict():
                
        last_period = end - start
        last_start = start - last_period
        last_end = start
        if hospital is None:
            kwargs = {}
        else:
            kwargs = {"hospital":hospital}
            
        if code is not None:
            if code=="yellow":
                kwargs["triage_code"] = TriageCode.get_yellow()
            if code=="green":
                kwargs["triage_code"] = TriageCode.get_green()
            if code=="white":
                kwargs["triage_code"] = TriageCode.get_white()
                
        wait_q_filter = TriageAccess.get_q_filter_for_exit_interval(from_hours=from_hours,to_hours=to_hours)
            
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
            
            value = method(wait_q_filter,access_date__gte=start,access_date__lte=end,**kwargs)
            last = method(wait_q_filter,access_date__gte=last_start,access_date__lt=last_end,**kwargs)
            diff = value.count() - last.count()
            
            cards[name] = {
                "value" : value.count(),
                "diff" : diff,
                "diff_formatted" : "("+sign_format[diff>=0]+str(diff)+")",
                "diff_class" : class_format[diff>=0],
            }
        
        return cards
    
    @classmethod
    def get_storico_big_graph(cls,start:datetime.date,end:datetime.date,code=None,from_hours=None,to_hours=None,hospital:Hospital=None)->dict():
        import json
        from .utils import timesteps_builder
        ## See https://www.chartjs.org/docs/latest/, 
        # https://www.chartjs.org/docs/latest/developers/updates.html, 
        # https://demos.creative-tim.com/argon-dashboard-pro-react/?_ga=2.191324073.2076643225.1638138645-576346499.1636196270#/documentation/charts
        
        if hospital is None:
            kwargs = {}
        else:
            kwargs = {"hospital":hospital}
            
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
        
        wait_q_filter = TriageAccess.get_q_filter_for_exit_interval(from_hours=from_hours,to_hours=to_hours)
        
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
            data = method(wait_q_filter,access_date__gte=start_date,access_date__lte=end_date,**kwargs)
            # data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
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
            data = method(wait_q_filter,access_date__gte=start_date,access_date__lte=end_date,**kwargs)
            # data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
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
            data = method(wait_q_filter,access_date__gte=start_date,access_date__lte=end_date,**kwargs)
            # data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
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
    def get_storico_bar_graph(cls,start:datetime.date,end:datetime.date,code=None,from_hours=None,to_hours=None,hospital:Hospital=None):
        from django.db.models import Count
        
        if hospital is None:
            kwargs = {}
        else:
            kwargs = {"hospital":hospital}
            
        name_methods = {
            "yellow":"yellows",
            "green":"greens",
            "white":"whites",
            None:"filter",
        }
        method = getattr(TriageAccess,name_methods[code])
        
        data = method(access_date__gte=start,access_date__lte=end,**kwargs)
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
    def get_storico_table(cls,request,start:datetime.date,end:datetime.date,code=None,from_hours=None,to_hours=None,hospital:Hospital=None):        
        if hospital is None:
            kwargs = {}
        else:
            kwargs = {"hospital":hospital}
            
        name_methods = {
            "yellow":"yellows",
            "green":"greens",
            "white":"whites",
            None:"filter",
        }
        method = getattr(TriageAccess,name_methods[code])

                
        data = method(access_date__gte=start,access_date__lte=end,**kwargs)
        data = TriageAccess.filter_for_exit_interval(data,from_hours=from_hours,to_hours=to_hours)
        data = data.order_by("access_date")
        table = cls.get_table(request,data)
        return table
    
    @classmethod
    def get_table(cls,request,data):
        import re
        from django.template.loader import render_to_string
        
        units = {}
        units["temperature"] = "°C"
        units["pressure"] = "mmHg"
        units["heartrate"] = "bpm"
        
        for item in data:
            item.access_date_cache = item.access_date.strftime("%x %X")
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
        },request=request)
        table = re.sub(r'\s*\n\s*', ' ', table).strip()
        return str(table)

class SetLiveAccessStatus(APIView):
    def post(self, request, *args, **kwargs):        
        user = AppUser.get_or_create_from_parent(request.user)        
        hospital = user.dashboard_hospital
        
        access_id = request.POST.get("access_id")
        action = request.POST.get("action")
        
        access = get_object_or_404(TriageAccess,id=access_id)
        if action=="enter":
            access.exit_date = None
        elif action=="exit":
            access.exit_date = timezone.localtime()
        access.save()
        
        ## Rebuild the table
        
        now = timezone.localtime()
        one_hour_ago = relativedelta(hours=1)
        cards = GetLiveData.get_live_cards(start=None,end=now,diff_period=one_hour_ago,hospital=hospital)
        live_table = GetLiveData.get_live_table(
            request,
            hospital,
            )
        return JsonResponse({
            'success': True,
            "cards":cards,
            "live_table":live_table,
            })

class SetStoricoAccessStatus(APIView):
    def post(self, request, *args, **kwargs):
        
        access_id = request.POST.get("access_id")
        action = request.POST.get("action")
        
        access = get_object_or_404(TriageAccess,id=access_id)
        if action=="enter":
            access.exit_date = None
        elif action=="exit":
            access.exit_date = timezone.localtime()
        access.save()
        return JsonResponse({
            'success': True,
            })
