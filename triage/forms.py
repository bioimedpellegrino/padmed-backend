from django import forms
from .models import Patient
from django.core.validators import RegexValidator

fiscal_code_validator = RegexValidator(r"^([A-Z]{6}[0-9LMNPQRSTUV]{2}[ABCDEHLMPRST]{1}[0-9LMNPQRSTUV]{2}[A-Z]{1}[0-9LMNPQRSTUV]{3}[A-Z]{1})$|([0-9]{11})$", "Il codice fiscale inserito non è valido.") 

class PatientForm(forms.Form):
    fiscal_code = forms.CharField(label='Codice Fiscale', max_length=16, validators=[fiscal_code_validator])
    
    class Media:
        css = {'all': ('/staticfiles/assets/css/argon-dashboard.css')}

class AnagraficaForm(forms.ModelForm):
    class Media:
        from .models import DeclaredAnagrafica
        model = DeclaredAnagrafica
        exclude = ("id","expired","created","modified")
        labels = {
            "patient":"Paziente",
            "birth_year":"Anno di nascita",
            "gender":"Sesso",
            "height":"Altezza",
            "smoking":"Fumatore",
            "diabetes":"Diabetico",
            "bloodpressuremedication":"Assumi antipertensivi",
        }
    