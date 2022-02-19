from django.contrib import admin
from .models import *
# Register your models here.


class DeepAffexPointAdmin(admin.ModelAdmin):
    list_display = ['signal_key', 'signal_name', 'signal_unit', 'signal_config', 'multiplier']
    list_filter = ['signal_config']


admin.site.register(DeepAffexPoint, DeepAffexPointAdmin)
