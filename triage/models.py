import datetime
import json
import os
import base64

from generic.models import City, Province, Country

from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.fields import related
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import pre_save, post_init


GENDER = (
    ('M', 'M'),
    ('F', 'F'),
    ('O', 'O'),
)
NATIONALITY = (
    ('italian', 'italian'),
    ('foreign', 'foreign'),
)

TRIAGE_CODES = (
    ('WHITE', 'WHITE'),
    ('GREEN', 'GREEN'),
    ('YELLOW', 'YELLOW')
)
        
class Hospital(models.Model):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=512, default="")
    full_address = models.TextField(blank=True, null=True, default="")
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE, related_name="hospital_city")
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE, related_name="hospital_province")
    country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.CASCADE, related_name="hospital_country")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Ospedale"
        verbose_name_plural = "Ospedali"
    

class Patient(models.Model):
    """
    Model Patient
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    fiscal_code = models.CharField(blank=True, null=True, max_length=512, default="")
    first_name = models.CharField(blank=True, null=True, max_length=512, default="")
    middle_name = models.CharField(blank=True, null=True, max_length=512, default="")
    last_name = models.CharField(blank=True, null=True, max_length=512, default="")
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(blank=True, null=True, max_length=512, default="")
    note = models.TextField(blank=True, null=True, default="")
    gender = models.CharField(blank=True, null=True, max_length=1, choices=GENDER)
    phone = models.CharField(blank=True, null=True, max_length=512, default="")
    email = models.CharField(blank=True, null=True, max_length=512, default="")
    nationality = models.CharField(blank=True, null=True, max_length=512, default="italian", choices=NATIONALITY)
    has_accept_privacy = models.BooleanField(default=False)
    lang = models.CharField(default='it', max_length=5)
    full_address = models.TextField(blank=True, null=True, default="")
    residence_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE, related_name="residence_city")
    residence_city_code = models.CharField(blank=True, null=True, max_length=512, default="")
    residence_province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE, related_name="residence_province")
    residence_zip_code = models.CharField(blank=True, null=True, max_length=512, default="")
    residence_country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.CASCADE, related_name="residence_country")
    domicile_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE, related_name="domicile_city")
    domicile_city_code = models.CharField(blank=True, null=True, max_length=512, default="")
    domicile_province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE, related_name="domicile_province")
    domicile_zip_code = models.CharField(blank=True, null=True, max_length=512, default="")
    domicile_country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.CASCADE, related_name="domicile_country")
    hospital = models.ForeignKey(Hospital, blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.fiscal_code
    
    class Meta:
        verbose_name = "Paziente"
        verbose_name_plural = "Pazienti"
        ordering = ('last_name',)

class TriageCode(models.Model):
    
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=32, blank=True, null=True, choices=TRIAGE_CODES)
    
    def __str__(self):
        return self.code
        
    class Meta:
        verbose_name = "Codice triage"
        verbose_name_plural = "Codici triage"

class TriageAccessReason(models.Model):
    
    id = models.AutoField(primary_key=True)
    hospital = models.ForeignKey(Hospital, blank=True, null=True, on_delete=models.CASCADE)
    reason = models.CharField(blank=True, null=True, max_length=512, default="")
    related_code = models.ForeignKey(TriageCode, blank=True, null=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.reason
    
    class Meta:
        verbose_name = "Motivo accesso"
        verbose_name_plural = "Motivi accesso al pronto soccorso"


class TriageAccess(models.Model):
    
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, blank=True, null=True, related_name='accesses', on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, blank=True, null=True, related_name='accesses', on_delete=models.CASCADE)
    triage_code = models.ForeignKey(TriageCode, blank=True, null=True, on_delete=models.CASCADE)
    access_reason = models.ForeignKey(TriageAccessReason, blank=True, null=True, on_delete=models.CASCADE)
    access_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = "Accesso"
        verbose_name_plural = "Accessi al pronto soccorso"
