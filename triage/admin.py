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

admin.site.register(Patient, PatientAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(Country, CountryAdmin)