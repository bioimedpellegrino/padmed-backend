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

WHITE = 'WHITE'
GREEN = 'GREEN'
YELLOW ='YELLOW'
TRIAGE_CODES = (
    (WHITE, 'WHITE'),
    (GREEN, 'GREEN'),
    (YELLOW, 'YELLOW')
)
        
class Hospital(models.Model):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, max_length=512, default="")
    full_address = models.TextField(blank=True, null=True, default="")
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT, related_name="hospital_city")
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.PROTECT, related_name="hospital_province")
    country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.PROTECT, related_name="hospital_country")
    
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
    residence_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT, related_name="residence_city")
    residence_city_code = models.CharField(blank=True, null=True, max_length=512, default="")
    residence_province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.PROTECT, related_name="residence_province")
    residence_zip_code = models.CharField(blank=True, null=True, max_length=512, default="")
    residence_country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.PROTECT, related_name="residence_country")
    domicile_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT, related_name="domicile_city")
    domicile_city_code = models.CharField(blank=True, null=True, max_length=512, default="")
    domicile_province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.PROTECT, related_name="domicile_province")
    domicile_zip_code = models.CharField(blank=True, null=True, max_length=512, default="")
    domicile_country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.PROTECT, related_name="domicile_country")
    hospital = models.ForeignKey(Hospital, blank=True, null=True, on_delete=models.PROTECT)
    
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
    
    @classmethod
    def get_white(cls):
        return cls.objects.get(code=WHITE)
    @classmethod
    def get_green(cls):
        return cls.objects.get(code=GREEN)
    @classmethod
    def get_yellow(cls):
        return cls.objects.get(code=YELLOW)

class TriageAccessReason(models.Model):
    
    id = models.AutoField(primary_key=True)
    hospital = models.ForeignKey(Hospital, blank=True, null=True, on_delete=models.CASCADE)
    reason = models.CharField(blank=True, null=True, max_length=512, default="")
    related_code = models.ForeignKey(TriageCode, blank=True, null=True, on_delete=models.PROTECT)
    
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
    triage_code = models.ForeignKey(TriageCode, blank=True, null=True, on_delete=models.PROTECT)
    access_reason = models.ForeignKey(TriageAccessReason, blank=True, null=True, on_delete=models.PROTECT)
    access_date = models.DateTimeField(blank=True, null=True)
    exit_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.id, self.patient)
    
    @classmethod
    def whites(cls,exclude=[],**kwargs):
        objs = cls.objects.filter(triage_code=TriageCode.get_white())
        objs = objs.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def greens(cls,exclude=[],**kwargs):
        objs = cls.objects.filter(triage_code=TriageCode.get_green())
        objs = objs.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def yellows(cls,exclude=[],**kwargs):
        objs = cls.objects.filter(triage_code=TriageCode.get_yellow())
        objs = objs.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    
    class Meta:
        verbose_name = "Accesso"
        verbose_name_plural = "Accessi al pronto soccorso"
        
class PatientVideo(models.Model):
    
    id = models.AutoField(primary_key=True)
    triage_access = models.ForeignKey(TriageAccess, blank=True, null=True, on_delete=models.CASCADE)
    video = models.FileField(blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.triage_access)
    
    class Meta:
        verbose_name = "Video Misura"
        verbose_name_plural = "Video Misura"
        
class PatientMeasureResult(models.Model):
    
    id = models.AutoField(primary_key=True)
    measurement_id = models.CharField(max_length=2000, blank=True, null=True, default="")
    patient_video = models.ForeignKey(PatientVideo, blank=True, null=True, on_delete=models.CASCADE)
    result = models.TextField(blank=True, null=True, default="{}")
    
    def __str__(self):
        return "{} - {}".format(self.id, self.measurement_id)
    
    class Meta:
        verbose_name = "Esito misurazioni"
        verbose_name_plural = "Esiti misurazioni"