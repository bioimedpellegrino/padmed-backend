import datetime
import json
import os
import base64
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
class GenericPlace(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True, default="", max_length=2000)
    short_name = models.CharField(blank=True, null=True, max_length=2000)
    code = models.CharField(blank=True, null=True, max_length=2000)
    
    class Meta:
        abstract = True
class Country(GenericPlace):
    """
    Model Country
    """
    class Meta:
        verbose_name = "Nazione"
        verbose_name_plural = "Nazioni" 
class Province(GenericPlace):
    """
    Model Province
    """
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = "Provincia"
        verbose_name = "Province"
class City(GenericPlace):
    "Model City"
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = "Città"
        verbose_name_plural = "Città"
class Hospital(models.Model):
    pass

class Patient(models.Model):
    """
    Model Patient
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    fiscal_code = models.TextField(blank=True, null=True, default="")
    first_name = models.TextField(blank=True, null=True, default="")
    middle_name = models.TextField(blank=True, null=True, default="")
    last_name = models.TextField(blank=True, null=True, default="")
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.TextField(blank=True, null=True, default="")
    gender = models.CharField(blank=True, null=True, max_length=1, choices=GENDER)
    phone = models.TextField(blank=True, null=True, default="")
    email = models.TextField(blank=True, null=True, default="")
    nationality = models.TextField(blank=True, null=True, default="italian", choices=NATIONALITY)
    has_accept_privacy = models.BooleanField(default=False)
    lang = models.CharField(default='it', max_length=5)
    full_address = models.TextField(blank=True, null=True, default="")
    residence_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE, related_name="residence_city")
    residence_city_code = models.TextField(blank=True, null=True, default="")
    residence_province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE, related_name="residence_province")
    residence_zip_code = models.TextField(blank=True, null=True, default="")
    residence_country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.CASCADE, related_name="residence_country")
    domicile_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.CASCADE, related_name="domicile_city")
    domicile_city_code = models.TextField(blank=True, null=True, default="")
    domicile_province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.CASCADE, related_name="domicile_province")
    domicile_zip_code = models.TextField(blank=True, null=True, default="")
    domicile_country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.CASCADE, related_name="domicile_country")
    hospital = models.ForeignKey(Hospital, blank=True, null=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Paziente"
        verbose_name_plural = "Pazienti"
        ordering = ('last_name',)
        