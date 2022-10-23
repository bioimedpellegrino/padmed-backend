from django.contrib import admin
from .models import VideoSettings, FilterPreview


class VideoSettingsAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'totem', 'is_active', ]
    list_filter = ['totem', 'is_active']

admin.site.register(VideoSettings, VideoSettingsAdmin)
admin.site.register(FilterPreview)