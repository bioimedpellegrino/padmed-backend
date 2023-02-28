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
    
    @property
    def get_settings(self):
        
        return {
            "camera_rotation": self.camera_rotation,
            "adjust_color": self.red_value != 10 or self.blue_value != 10 or self.green_value != 10,
            "red_value": self.red_value / 10,
            "blue_value": self.blue_value / 10,
            "green_value": self.green_value / 10,
            "color": self.color / 1000,
            "contrast": self.contrast / 10,
            "brightness": self.brightness / 10,
            "sharpness": self.sharpness / 10
        }
        
class FilterPreview(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    video_setting = models.ForeignKey(VideoSettings, blank=True, null=True, on_delete=models.SET_NULL)
    original_image = models.ImageField(upload_to="original_image")
    filtered_image = models.ImageField(upload_to="filtered_image")
    
    def __str__(self):
        return "{}".format(self.video_setting.pk)
    
    def save(self, *args, **kwargs):
        
        from PIL import Image
        from io import BytesIO
        from django.core.files import File
        from triage.utils import frame_enhance

        if self.original_image and self.video_setting:
            original_image = Image.open(self.original_image).convert('RGB')
            if self.filtered_image:
                import os
                try:
                    os.remove(self.filtered_image.path)
                except:
                    pass
            filtered_image = frame_enhance(original_image, self.video_setting.get_settings, convert_from_array=False, return_pil_image=True)
            blob = BytesIO()
            filtered_image.save(blob, 'JPEG')
            name = self.original_image.name.split("/")[-1]
            self.filtered_image.save(name, File(blob), save=False)
            
        super(FilterPreview, self).save(*args, **kwargs) # Call the "real" save() method.

    class Meta:
        verbose_name = "Anteprima filtri"
        verbose_name_plural = "Anteprime filtri"
    
    
    