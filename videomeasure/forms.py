from django import forms
from .models import VideoSettings, ROTATION_CHOICES

class VideoSettingForm(forms.ModelForm):
    class Meta:
        model = VideoSettings
        fields = (
            'totem',
            'is_active',
            'name',
            'camera_rotation',
            'red_value',
            'blue_value',
            'green_value',
            'color',
            'contrast',
            'brightness',
            'sharpness'
        )
        widgets = {
            'red_value': forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}),
            'blue_value' : forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}), 
            'green_value' : forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}),
            'color': forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}),
            'contrast': forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}),
            'brightness': forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}), 
            'sharpness': forms.TextInput(attrs={'type': 'range','min':1,'max':10, 'default': 1}),
        }
        labels = {
            "is_active": "Attiva",
            "camera_rotation":"Rotazione camera",
            "red_value":"Guadagno canale R",
            "blue_value":"Guadagno canale B",
            "green_value":"Guadagno canale G",
            "color":"Guadagno colore",
            "contrast":"Guadagno contrasto",
            "brightness":"Luminosità",
            "sharpness":"Nitidezza",
        }
        required = (
            'totem',
            'camera_rotation',
            'red_value',
            'blue_value',
            'green_value',
            'color',
            'contrast',
            'brightness',
            'sharpness'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
            
    class Media:
        css = {'all': ('/staticfiles/assets/css/argon-dashboard.css')}
    