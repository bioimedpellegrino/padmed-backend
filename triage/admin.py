from django.contrib import admin
from .models import *

class PatientAdmin(admin.ModelAdmin):
    list_display = ['fiscal_code', 'first_name', 'last_name', 'hospital']
    list_filter = ['hospital']

class HospitalAdmin(admin.ModelAdmin):
    pass

class TotemAdmin(admin.ModelAdmin):
    pass

class CityAdmin(admin.ModelAdmin):
    pass

class ProvinceAdmin(admin.ModelAdmin):
    pass

class CountryAdmin(admin.ModelAdmin):
    pass

class TriageCodeAdmin(admin.ModelAdmin):
    pass

class TriageAccessReasonAdmin(admin.ModelAdmin):
    list_display = ['reason', 'order']
    list_filter = ['hospital', 'related_code']

class TriageAccessAdmin(admin.ModelAdmin):
    list_display = ['created','patient','triage_code','access_reason','access_date']
    list_filter = ['patient', 'hospital', 'totem', 'triage_code', 'access_reason']

class PatientVideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'triage_access']

class PatientMeasureResultAdmin(admin.ModelAdmin):
    list_display = ['id','measurement_id','patient_video']

class MeasureLoggerAdmin(admin.ModelAdmin):
    list_display = ['pk', 'triage_access']

class DeclaredAnagraficaAdmin(admin.ModelAdmin):
    list_display = ['gender','height','weight','smoking','diabetes','bloodpressuremedication']
    list_filter = ['gender','smoking','diabetes','bloodpressuremedication', 'expired']

admin.site.register(Patient, PatientAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Totem, HospitalAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(TriageCode, TriageCodeAdmin)
admin.site.register(TriageAccessReason, TriageAccessReasonAdmin)
admin.site.register(TriageAccess, TriageAccessAdmin)
admin.site.register(PatientVideo, PatientVideoAdmin)
admin.site.register(PatientMeasureResult, PatientMeasureResultAdmin)
admin.site.register(MeasureLogger, MeasureLoggerAdmin)
admin.site.register(DeclaredAnagrafica, DeclaredAnagraficaAdmin)