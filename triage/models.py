import datetime
import json
import os
import base64
import pytz
from functools import lru_cache
from pprint import pprint
from dateutil.relativedelta import relativedelta

from generic.models import City, Province, Country

from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.fields import related
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import pre_save, post_init
from django.db.models.query import QuerySet


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
    birth_place_city = models.CharField(blank=True, null=True, max_length=512, default="")
    birth_place_province = models.CharField(blank=True, null=True, max_length=2000, default="")
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
    
    def save(self, *args, **kwargs):
        from codicefiscale import codicefiscale
        if self.fiscal_code and codicefiscale.is_valid(self.fiscal_code):
            decoded = codicefiscale.decode(self.fiscal_code)
            self.birth_date = decoded['birthdate'] if not self.birth_date else self.birth_date
            self.gender = decoded['sex'] if not self.gender else self.gender
            self.birth_place_city = decoded['birthplace']['name'] if not self.birth_place_city else self.birth_place_city
            self.birth_place_province = decoded['birthplace']['province'] if not self.birth_place_province else self.birth_place_province
        super(Patient, self).save(*args, **kwargs)

    
    
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
    
    @property
    def is_white(self)->bool:
        return self.triage_code == TriageCode.get_white()
    @property
    def set_white(self):
        self.triage_code == TriageCode.get_white()
        self.save()
    @property
    def is_green(self)->bool:
        return self.triage_code == TriageCode.get_green()
    @property
    def set_green(self):
        self.triage_code == TriageCode.get_green()
        self.save()
    @property
    def is_yellow(self)->bool:
        return self.triage_code == TriageCode.get_yellow()
    @property
    def set_yellow(self):
        self.triage_code == TriageCode.get_yellow()
        self.save()
    
    @property
    def waiting_progress(self)->int:
        ## Qui si può mettere un sistema di calcolo del tempo medio (chesciato in qualche tabella e aggiornato di giorno in giorno)
        ## per sostituire settings.INIT_MAX_WAITING_SECONDS e dare all'operatore una idea più realistica e utile del tempo di 
        ## attesa 
        seconds = self.whaiting_time
        waiting_progress = float(seconds)/settings.INIT_MAX_WAITING_SECONDS
        return int(waiting_progress)
    @property
    def waiting_time(self)->relativedelta:
        from dateutil.relativedelta import relativedelta as rd
        access_date = self.access_date
        tz = pytz.timezone('Europe/Rome')
        rome_now = datetime.datetime.now(tz)
        waiting_time = rd(rome_now,access_date)
        ## TODO: formatta waiting_time
        return waiting_time
        
        
    @classmethod
    def whites(cls,exclude=[],**kwargs)->QuerySet:
        objs = cls.objects.filter(triage_code=TriageCode.get_white())
        objs = objs.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def greens(cls,exclude=[],**kwargs)->QuerySet:
        objs = cls.objects.filter(triage_code=TriageCode.get_green())
        objs = objs.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def yellows(cls,exclude=[],**kwargs)->QuerySet:
        objs = cls.objects.filter(triage_code=TriageCode.get_yellow())
        objs = objs.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def filter(cls,*args,**kwargs):
        return cls.objects.filter(*args,**kwargs)
    
    @classmethod
    def ordered_items(cls,exclude=[],**kwargs)->QuerySet:
        ## Implement here the ordering policy of the hospital ##
        objs = cls.objects.all().order_by("access_date")
        
        objs = cls.objects.filter(**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        
        return objs
    
    @classmethod
    def filter_for_exit_interval(cls,value,last=None,from_hours=None,to_hours=None):
        from datetime import timedelta
        from django.db.models import F
        filter_dict = {}
        if from_hours:
            filter_dict["exit_date__gte"] = F("access_date")+timedelta(hours=from_hours)
        if to_hours:
            filter_dict["exit_date__lt"] = F("access_date")+timedelta(hours=to_hours)
        
        value = value.filter(**filter_dict)
        if last is not None:
            last = last.filter(**filter_dict)
            return value, last
        return value
    
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
    measure_short = models.TextField(blank=True, null=True, default="{}")
    
    def __str__(self):
        return "{} - {}".format(self.id, self.measurement_id)
    
    class Meta:
        verbose_name = "Esito misurazioni"
        verbose_name_plural = "Esiti misurazioni"
    
    @property
    @lru_cache(maxsize=None)
    def get_result(self):
        import ast
        result = ast.literal_eval(self.result)
        return result

    @property
    @lru_cache(maxsize=None)
    def get_hresult(self):
        from random import randrange
        import statistics
        result = self.get_result
        hresult = {
            "heart_rate":{},
            "pressure":{"min":{},"max":{}},
            "temperature":{}
        }
            
        ## Temperature
        # data = result["Results"]["HR_BPM"]["Data"]
        # multiplier = result["Results"]["HR_BPM"]["Multiplier"]
        # unit = result["SignalUnits"]["HR_BPM"]
        hresult["temperature"]["mean"] = randrange(27,42)
        hresult["temperature"]["stdev"] = 1
        hresult["temperature"]["unit"] = "°C"
        if hresult["temperature"]["mean"] < 27:
            hresult["temperature"]["alarm"] = 3
            hresult["temperature"]["order"] = "%s%02d"%(0, hresult["temperature"]["mean"])
        elif hresult["temperature"]["mean"] < 33:
            hresult["temperature"]["alarm"] = 2
            hresult["temperature"]["order"] = "%s%02d"%(1, hresult["temperature"]["mean"])
        elif hresult["temperature"]["mean"] < 35:
            hresult["temperature"]["alarm"] = 1
            hresult["temperature"]["order"] = "%s%02d"%(2, hresult["temperature"]["mean"])
        elif hresult["temperature"]["mean"] < 37:
            hresult["temperature"]["alarm"] = 0
            hresult["temperature"]["order"] = "%s%02d"%(3, 50-hresult["temperature"]["mean"])
        elif hresult["temperature"]["mean"] < 40:
            hresult["temperature"]["alarm"] = 1
            hresult["temperature"]["order"] = "%s%02d"%(2, 50-hresult["temperature"]["mean"])
        elif hresult["temperature"]["mean"] < 41.1:
            hresult["temperature"]["alarm"] = 2
            hresult["temperature"]["order"] = "%s%02d"%(1, 50-hresult["temperature"]["mean"])
        elif hresult["temperature"]["mean"] >= 41.1:
            hresult["temperature"]["alarm"] = 3
            hresult["temperature"]["order"] = "%s%02d"%(0, 50-hresult["temperature"]["mean"])
            
        ## Blood pressure
        # data = result["Results"]["HR_BPM"]["Data"]
        # multiplier = result["Results"]["HR_BPM"]["Multiplier"]
        # unit = result["SignalUnits"]["HR_BPM"]
        hresult["pressure"]["min"]["mean"] = randrange(40,200)
        hresult["pressure"]["min"]["stdev"] = 3
        hresult["pressure"]["min"]["unit"] = "mmHg"
        hresult["pressure"]["max"]["mean"] = randrange(70,220)
        hresult["pressure"]["max"]["stdev"] = 3
        hresult["pressure"]["max"]["unit"] = "mmHg"
        pmin = hresult["pressure"]["min"]["mean"]
        pmax = hresult["pressure"]["max"]["mean"]
        if pmin < 50:
            min_alarm = 3
        elif pmin < 60:
            min_alarm = 2
        elif pmin < 65:
            min_alarm = 1
        elif pmin < 85:
            min_alarm = 0
        elif pmin < 100:
            min_alarm = 1
        elif pmin < 120:
            min_alarm = 2
        elif pmin >= 120:
            min_alarm = 3
        if pmax < 70:
            max_alarm = 3
        elif pmax < 90:
            max_alarm = 2
        elif pmax < 100:
            max_alarm = 1
        elif pmax < 130:
            max_alarm = 0
        elif pmax < 160:
            max_alarm = 1
        elif pmax < 180:
            max_alarm = 2
        elif pmax >= 180:
            max_alarm = 3
        pmin = hresult["pressure"]["alarm"] = max(min_alarm,max_alarm)
        hresult["pressure"]["order"] = "%s%03d%03d"%(3-hresult["pressure"]["alarm"],pmin,pmax)
            
        ## Heart rate
        data = result["Results"]["HR_BPM"][0]["Data"]
        multiplier = result["Results"]["HR_BPM"][0]["Multiplier"]
        unit = result["SignalUnits"]["HR_BPM"]
        hresult["heart_rate"]["mean"] = round(statistics.fmean(data)/multiplier)
        hresult["heart_rate"]["stdev"] = round(statistics.stdev(data)/multiplier) # TODO: add SDR information
        hresult["heart_rate"]["unit"] = unit
        if hresult["heart_rate"]["mean"] < 40:
            hresult["heart_rate"]["alarm"] = 3
            hresult["heart_rate"]["order"] = "%s%03d"%(0, hresult["heart_rate"]["mean"])
        elif hresult["heart_rate"]["mean"] < 50:
            hresult["heart_rate"]["alarm"] = 2
            hresult["heart_rate"]["order"] = "%s%03d"%(1, hresult["heart_rate"]["mean"])
        elif hresult["heart_rate"]["mean"] < 60:
            hresult["heart_rate"]["alarm"] = 1
            hresult["heart_rate"]["order"] = "%s%03d"%(2, hresult["heart_rate"]["mean"])
        elif hresult["heart_rate"]["mean"] < 100:
            hresult["heart_rate"]["alarm"] = 0
            hresult["heart_rate"]["order"] = "%s%03d"%(3, 130-hresult["heart_rate"]["mean"])
        elif hresult["heart_rate"]["mean"] < 110:
            hresult["heart_rate"]["alarm"] = 1
            hresult["heart_rate"]["order"] = "%s%03d"%(2, 130-hresult["heart_rate"]["mean"])
        elif hresult["heart_rate"]["mean"] < 120:
            hresult["heart_rate"]["alarm"] = 2
            hresult["heart_rate"]["order"] = "%s%03d"%(1, 130-hresult["heart_rate"]["mean"])
        elif hresult["heart_rate"]["mean"] >= 120:
            hresult["heart_rate"]["alarm"] = 3
            hresult["heart_rate"]["order"] = "%s%03d"%(0, 130-hresult["heart_rate"]["mean"])
        
        return hresult