import datetime
import json
import os
import base64
import pytz
from functools import lru_cache
from pprint import pprint
from dateutil.relativedelta import relativedelta

from generic.models import City, Province, Country
from app.models import RestrictedClass

from django.db import models
from django.contrib.auth.models import User
from django.db.models import F,Q
from django.db.models.fields import related
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import pre_save, post_init
from django.db.models.query import QuerySet
from django.utils import timezone


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
        
class Hospital(RestrictedClass):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(blank=True,null=True,max_length=512,default="")
    logo = models.ImageField(verbose_name="Logo",null=True,blank=True,upload_to='triage/hospital/logos')
    full_address = models.TextField(blank=True, null=True, default="")
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT, related_name="hospital_city")
    province = models.ForeignKey(Province, blank=True, null=True, on_delete=models.PROTECT, related_name="hospital_province")
    country = models.ForeignKey(Country, blank=True, null=True,on_delete=models.PROTECT, related_name="hospital_country")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Ospedale"
        verbose_name_plural = "Ospedali"
    
    @property
    def fancy_address(self):
        result = ""
        if self.full_address:
            result += self.full_address
        if self.city:
            result += " - "+self.city
        if self.province:
            result += " ("+self.province+")"
        if self.country:
            result += " - "+self.country
        return result
    
    @property
    def access_patient_set(self):
        patients_pk = self.accesses.values_list("patient__pk")
        return Patient.objects.filter(pk__in=patients_pk)
        
class Totem(models.Model):
    name = models.CharField(verbose_name="Nome",blank=True,null=True,max_length=512,default="")
    code = models.UUIDField(verbose_name="Codice totem fisico",auto_created=True,null=True,blank=True,unique=True)
    description = models.TextField(verbose_name="Descrizione",blank=True,null=True)
    logs = models.TextField(verbose_name="Storico",blank=True,null=True)
    hospital = models.ForeignKey(Hospital,blank=True,null=True,on_delete=models.SET_NULL)
    working = models.BooleanField(verbose_name="Funzionante",default=True)
    activation_date = models.DateTimeField(verbose_name="Data di attivazione",blank=True, null=True)
    disposal_date = models.DateTimeField(verbose_name="Data di dismissione",blank=True, null=True)
    
    created = models.DateTimeField(verbose_name="Data di creazione",auto_now_add=True)
    modified = models.DateTimeField(verbose_name="Data di creazione",blank=True, null=True,auto_now=True)

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    """
    Model Patient
    """
    id = models.AutoField(primary_key=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    totem = models.ForeignKey(Totem, blank=True, null=True, related_name='accesses', on_delete=models.CASCADE)
    triage_code = models.ForeignKey(TriageCode, blank=True, null=True, on_delete=models.PROTECT)
    access_reason = models.ForeignKey(TriageAccessReason, blank=True, null=True, on_delete=models.PROTECT)
    access_date = models.DateTimeField(blank=True, null=True)
    exit_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.id, self.patient)
    @property
    def h_str(self):
        return "{} - {}".format(self.patient, self.local_access_date.strftime("%c"))
        
    # @property
    # def local_access_date(self):
    # # https://docs.djangoproject.com/en/3.2/topics/i18n/formatting/
    #     import pytz
    #     local_timezone = pytz.timezone(settings.TIME_ZONE)
    #     local_access_date = self.access_date.astimezone(local_timezone)
    #     return local_access_date
        
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
        now = timezone.localtime()
        waiting_time = rd(now,access_date)
        ## TODO: formatta waiting_time
        return waiting_time
        
    @property
    def last_hresult(self):
        last_result = None
        video = self.patientvideo_set.last()
        if video:
            measure = video.patientmeasureresult_set.last()
            if measure:
                last_result = measure.get_hresult
        return last_result
    @property
    def result_set(self):
        videos = self.patientvideo_set.all()
        result_set = PatientMeasureResult.objects.filter(patient_video__in=videos)
        return result_set
        
    @classmethod
    def whites(cls,*args,exclude=[],**kwargs)->QuerySet:
        objs = cls.objects.filter(triage_code=TriageCode.get_white())
        objs = objs.filter(*args,**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def greens(cls,*args,exclude=[],**kwargs)->QuerySet:
        objs = cls.objects.filter(triage_code=TriageCode.get_green())
        objs = objs.filter(*args,**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def yellows(cls,*args,exclude=[],**kwargs)->QuerySet:
        objs = cls.objects.filter(triage_code=TriageCode.get_yellow())
        objs = objs.filter(*args,**kwargs)
        for exc in exclude:
            objs = objs.exclude(**exc)
        return objs
    @classmethod
    def filter(cls,q_filter=None,*args,**kwargs):
        return cls.objects.filter(*args,**kwargs)
    
    @classmethod
    def ordered_items(cls,exclude=[],q_filter=None,**kwargs)->QuerySet:
        ## Implement here the ordering policy of the hospital ##
        objs = cls.objects.all().order_by("access_date")
        
        objs = cls.objects.filter(**kwargs)
        if q_filter is not None:
            objs = objs.filter(q_filter)
        for exc in exclude:
            objs = objs.exclude(**exc)
        
        return objs
    
    @classmethod
    def get_q_filter_for_exit_interval(cls,from_hours=None,to_hours=None):
        from datetime import timedelta
        now = timezone.localtime()
        
        q_filter = Q()
        if from_hours:
            q_filter = q_filter & (
                (
                    Q(exit_date__isnull=False) &
                    Q(exit_date__gte = F("access_date")+timedelta(hours=from_hours))
                ) |                
                (
                    Q(exit_date__isnull=True) &
                    Q(access_date__lte=now-timedelta(hours=from_hours))
                )
            )
        if to_hours:
            q_filter = q_filter & (
                (
                    Q(exit_date__isnull=False) &
                    Q(exit_date__lt = F("access_date")+timedelta(hours=to_hours))
                ) |                
                (
                    Q(exit_date__isnull=True) &
                    Q(access_date__gt=now-timedelta(hours=to_hours))
                )
            )
        
        return q_filter
    
    @classmethod
    def filter_for_exit_interval(cls,value,from_hours=None,to_hours=None):
        q_filter = cls.get_q_filter_for_exit_interval(from_hours=from_hours,to_hours=to_hours)
        value = value.filter(q_filter)
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
    
class MeasureLogger(models.Model):
    
    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    triage_access = models.ForeignKey(TriageAccess, blank=True, null=True, on_delete=models.CASCADE)
    log = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return "{}".format(self.id)
    
    class Meta:
        verbose_name = "Log Misurazione"
        verbose_name_plural = "Logs Misurazioni"
        
    def add_log(self, text):
        if self.log:
            self.log += "\n" + text
            self.save()
        else:
            self.log = text
            self.save()