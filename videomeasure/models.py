from email.policy import default
from tabnanny import verbose
from django.db import models
from triage.models import Totem


ROTATION_CHOICES = ((0,'0'),(90,'90'),(-90,'-90'),(180,'180'))

class VideoSettings(models.Model):
    """_summary_

    Args:
        VideoSettings (Models): Video camera settings
    """
    created = models.DateTimeField(verbose_name="Data di creazione",auto_now_add=True)
    modified = models.DateTimeField(verbose_name="Data di modifica",blank=True, null=True,auto_now=True)
    is_active = models.BooleanField(default=False, blank=True, null=True)
    totem = models.ForeignKey(Totem, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="Nome",blank=True,null=True, default="", max_length=2048)
    # Video settings
    camera_rotation = models.PositiveSmallIntegerField(default=0, choices=ROTATION_CHOICES, blank=True, null=True, verbose_name="Rotazione Camera")
    red_value = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Canale R")
    blue_value = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Canale B")
    green_value = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Canale G")
    color = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Colore")
    contrast = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Contrasto")
    brightness = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Luminosita")
    sharpness = models.PositiveSmallIntegerField(default=1, blank=True, null=True, verbose_name="Nitidezza")
    
    class Meta:
        verbose_name = "Impostazione video"
        verbose_name_plural = "Impostazioni video"
        
    def __str__(self):
        return "{}".format(self.id)
    
    def to_json(self):
        
        return {
            "id": self.id,
            "name": self.name,
            "created": self.created,
            "modified": self.modified,
            "is_active": self.is_active,
            "totem": self.totem,
            "camera_rotation": self.camera_rotation,
            "red_value": self.red_value,
            "blue_value": self.blue_value,
            "green_value": self.green_value,
            "color": self.color,
            "contrast": self.contrast,
            "brightness": self.brightness,
            "sharpness": self.sharpness
        }
    
    