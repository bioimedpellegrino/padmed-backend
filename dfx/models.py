from django.db import models
from statistics import mean


SIGNAL_CONFIG = (
    ("ALGORITHM", "ALGORITHM"),
    ("MODEL", "MODEL"),
    ("SOURCE", "SOURCE"),
    ("CLASSIFIER", "CLASSIFIER")
)

class DeepAffexPoint(models.Model):
    
    id = models.AutoField(primary_key=True)
    signal_key = models.CharField(max_length=32, null=True, blank=True, default="")
    signal_name = models.CharField(max_length=1024, null=True, blank=True, default="")
    signal_description = models.CharField(max_length=1024, null=True, blank=True, default="")
    signal_config = models.CharField(max_length=32, blank=True, null=True, choices=SIGNAL_CONFIG, default="")
    signal_unit = models.CharField(max_length=32, blank=True, null=True, default="")
    multiplier = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return self.signal_name
    
    def to_json(self):
        return {
            "signal_key": self.signal_key,
            "signal_name": self.signal_name,
            "signal_description": self.signal_description,
            "signal_config": self.signal_config,
            "signal_unit": self.signal_unit,
            "multiplier": self.multiplier
        }
    
    @property
    def compute_value(self, data):        
        value = round(mean(data)/self.multiplier, 2)
        return {
            "value": value,
            "unit": self.signal_unit,
            "name": self.signal_name
        }