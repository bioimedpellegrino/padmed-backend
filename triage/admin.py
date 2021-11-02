from django.contrib import admin
from .models import *

class PatientAdmin(admin.ModelAdmin):
    pass

class HospitalAdmin(admin.ModelAdmin):
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
    pass

class TriageAccessAdmin(admin.ModelAdmin):
    pass

class PatientVideoAdmin(admin.ModelAdmin):
    pass

class PatientMeasureResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(Patient, PatientAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(TriageCode, TriageCodeAdmin)
admin.site.register(TriageAccessReason, TriageAccessReasonAdmin)
admin.site.register(TriageAccess, TriageAccessAdmin)
admin.site.register(PatientVideo, PatientVideoAdmin)
admin.site.register(PatientMeasureResult, PatientMeasureResultAdmin)