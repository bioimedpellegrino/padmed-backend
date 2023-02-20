from django import forms
from .models import VideoSettings, FilterPreview

class FilterPreviewForm(forms.ModelForm):
    
    class Meta:
        model = FilterPreview
        fields = ('original_image',)
    class Media:
        css = {'all': ('/staticfiles/assets/css/argon-dashboard.css')}
    
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
            'red_value': forms.TextInput(attrs={'type': 'range','min':0,'max':100, 'default': 10}),
            'blue_value' : forms.TextInput(attrs={'type': 'range','min':0,'max':100, 'default': 10}), 
            'green_value' : forms.TextInput(attrs={'type': 'range','min':0,'max':100, 'default': 10}),
            'color': forms.TextInput(attrs={'type': 'range','min':0,'max':10000, 'default': 10}),
            'contrast': forms.TextInput(attrs={'type': 'range','min':0,'max':100, 'default': 10}),
            'brightness': forms.TextInput(attrs={'type': 'range','min':0,'max':100, 'default': 10}), 
            'sharpness': forms.TextInput(attrs={'type': 'range','min':0,'max':100, 'default': 10}),
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
    