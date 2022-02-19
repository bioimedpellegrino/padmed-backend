from django.contrib import admin
from .models import *
# Register your models here.


class DeepAffexPointAdmin(admin.ModelAdmin):
    list_display = ['signal_key', 'signal_name', 'signal_unit', 'signal_config', 'multiplier', 'is_measure']
    list_filter = ['signal_config', 'is_measure']


admin.site.register(DeepAffexPoint, DeepAffexPointAdmin)
