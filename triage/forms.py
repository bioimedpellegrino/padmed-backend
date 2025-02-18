from django import forms
from .models import Patient
from django.core.validators import RegexValidator

fiscal_code_validator = RegexValidator(r"^([A-Z]{6}[0-9LMNPQRSTUV]{2}[ABCDEHLMPRST]{1}[0-9LMNPQRSTUV]{2}[A-Z]{1}[0-9LMNPQRSTUV]{3}[A-Z]{1})$|([0-9]{11})$", "Il codice fiscale inserito non è valido.") 

class PatientForm(forms.Form):
    fiscal_code = forms.CharField(label='Codice Fiscale', max_length=16, validators=[fiscal_code_validator])
    
    class Media:
        css = {'all': ('/staticfiles/assets/css/argon-dashboard.css')}

class AnagraficaForm(forms.ModelForm):
    class Meta:
        from .models import DeclaredAnagrafica
        model = DeclaredAnagrafica
        fields = (
            'patient',
            'gender',
            'birth_year',
            'height',
            'weight',
            'smoking',
            'diabetes',
            'bloodpressuremedication',
            'is_bloodpressure',
            'is_asthmatic',
            'is_allergic'
        )
        widgets = {
            'patient': forms.HiddenInput(),
            'gender': forms.HiddenInput(),
            'birth_year': forms.HiddenInput(),
            'height': forms.TextInput(attrs={'type': 'range','min':130,'max':200}),
            'weight': forms.TextInput(attrs={'type': 'range','min':50,'max':150}),
        }
        labels = {
            "patient":"Paziente",
            "birth_year":"Anno di nascita",
            "gender":"Sesso",
            "height":"ALTEZZA",
            "weight":"PESO",
            "smoking":"FUMATORE",
            "diabetes":"DIABETICO",
            "bloodpressuremedication":"IPERTESO",
        }
        required = (
            'patient',
            'birth_year',
            'gender',
            'height',
            'weight',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.Meta.required:
            self.fields[field].required = True
    