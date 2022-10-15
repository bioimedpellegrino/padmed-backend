from keyword import kwlist
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from app.models import AppUser
from triage.models import Hospital, Totem
from .models import VideoSettings
from .forms import VideoSettingForm

from logger.utils import add_log

from rest_framework.views import APIView


class RedirectView(APIView):
    def get(self, request, *args, **kwargs):
        url_name = kwargs["url_name"]
        url_kwargs = kwargs.get("url_kwargs",{})
        return redirect(reverse(url_name,kwargs=url_kwargs))   

class VideoSettingsView(APIView):
    
    template_name = 'videosettings.html'
    
    def get(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        hospital = user.dashboard_hospital
        
        if not hospital:
            raise PermissionDenied("Questo Totem non ha un hospedale associato. Associare un ospedale al Totem o contattare l'assistenza.")
        
        video_settings = VideoSettings.objects.filter(totem__hospital=hospital)
        response = [video_setting.to_json() for video_setting in video_settings]
        
        return render(request, self.template_name, { 'settings': response })
    
class EditSettingView(APIView):
    
    template_name = 'editsetting.html'
    
    def get(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        hospital = user.dashboard_hospital
        setting_id = kwargs.get('setting_id', None)
            
        if not hospital:
            raise PermissionDenied("Questo Totem non ha un hospedale associato. Associare un ospedale al Totem o contattare l'assistenza.")
        
        if not setting_id:
            form = VideoSettingForm()
        else:
            setting = VideoSettings.objects.get(pk=setting_id)
            form = VideoSettingForm(instance=setting)

        return render(request, self.template_name, { 'form': form, 'user' : user })

    def post(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        
        form = VideoSettingForm(request.POST)
        if form.is_valid():
            setting, _created = VideoSettings.objects.get_or_create(name=form.cleaned_data['name'], totem=form.cleaned_data['totem'])
            setting.totem = form.cleaned_data['totem']
            setting.is_active = form.cleaned_data['is_active']
            setting.name = form.cleaned_data['name'].upper().strip()
            setting.camera_rotation = form.cleaned_data['camera_rotation']
            setting.red_value = form.cleaned_data['red_value']
            setting.blue_value = form.cleaned_data['blue_value']
            setting.green_value = form.cleaned_data['green_value']
            setting.color = form.cleaned_data['color']
            setting.contrast = form.cleaned_data['contrast']
            setting.brightness = form.cleaned_data['brightness']
            setting.sharpness = form.cleaned_data['sharpness']
            setting.save()
            
            #if is active, deactivate other setting
            if setting.is_active:
                VideoSettings.objects.filter(totem=setting.totem).exclude(pk=setting.pk).update(is_active=False)
                
            return HttpResponseRedirect(reverse('videosettings'))
        
        else:
            return render(request, self.template_name, { 'form': form, 'user' : user })
        

class DeleteSettingView(APIView):
        
    def post(self, request, *args, **kwargs):
        
        user = AppUser.get_or_create_from_parent(request.user)
        hospital = user.dashboard_hospital
        setting_id = kwargs.get('setting_id', None)
            
        if not hospital or not setting_id:
            raise PermissionDenied("Permesso negato.")
        
        VideoSettings.objects.get(pk=setting_id).delete()
        return HttpResponseRedirect(reverse('videosettings'))
        
        