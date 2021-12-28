
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import query
from django.forms import widgets
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.utils.translation import gettext_lazy as _

class DateRangeForm(forms.Form):
    from .models import TriageCode
    ## TODO: fix timezone problems https://stackoverflow.com/questions/30700039/how-to-use-datefield-in-a-django-form-in-a-timezone-aware-way
    start = forms.DateField(
        input_formats=["%Y-%m-%d",],
        label="Data inizio",
    )
    end = forms.DateField(
        label="Data fine",
    )
    
    code = forms.ChoiceField(
        choices=(
            (None,"----"),
            ("yellow","Gialli"),
            ("green","Verdi"),
            ("white","Bianchi"),
        ),
        label="Codice",
        required=False,
        )
    from_hours = forms.FloatField(
        label="Attesa minima (ore)",
        required=False,
        )
    to_hours = forms.FloatField(
        label="Attesa massima (ore)",
        required=False,
        )
    
    # ## Hidden inputs
    # start_cache = forms.DateField(
    #     widget=forms.HiddenInput(),
    #     required=False,
    # )
    # end_cache = forms.DateField(
    #     widget=forms.HiddenInput(),
    #     required=False,
    # )
    
    ## Crispy forms helper for formatting staff
    helper = FormHelper()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field,forms.DateField):
                visible.field.widget.input_type = "date"
                # visible.field.widget.attrs['class'] = 'datetimepicker'
        self.helper.layout = Layout(
            Row(
                Column('start', css_class='form-group col-xl-3 col-lg-4 mb-0'),
                Column('end', css_class='form-group col-xl-3 col-lg-4 mb-0'),
                Column('code', css_class='form-group col-xl-2 col-lg-4 mb-0'),
                Column('from_hours', css_class='form-group col-xl-2 col-lg-4 mb-0'),
                Column('to_hours', css_class='form-group col-xl-2 col-lg-4 mb-0'),
                css_class='form-row'
            )
        )
    
    def clean_from_hours(self):
        data = self.cleaned_data.get('from_hours', '')
        if not data:
            data = None
        return data
    
    def clean_to_hours(self):
        data = self.cleaned_data.get('to_hours', '')
        if not data:
            data = None
        return data
    
    def clean_code(self):
        data = self.cleaned_data.get('code', '')
        if not data:
            data = None
        return data

class AppUserEditForm(forms.ModelForm):
    
    class Meta(object):
        from app.models import AppUser
        model = AppUser
        fields = ['username','first_name','last_name','email',"img",'theme','_dashboard_options']
        widgets = {
            "_dashboard_options":forms.HiddenInput(),
        }
    ## Crispy forms helper for formatting staff
    helper = FormHelper()    
    
    # TODO: aggiungere Indicatori, Default incremento sulle cards, Default intervallo storico
    
    def __init__(self, *args, **kwargs):
        from crispy_forms.layout import Layout, Fieldset,HTML,Div
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field,forms.DateField):
                visible.field.widget.input_type = "date"
                
        self.helper.layout = Layout(
            HTML(
            """
                <h6 class="heading-small text-muted mb-4">Informazioni utente</h6>
            """
            ),
            Div(
                'username',
                'first_name',
                'last_name',
                'email',
                'img',
                css_class="pl-lg-4"
            ),
            HTML(
            """
                <hr class="my-4" />
                <h6 class="heading-small text-muted mb-4">Impostazioni di visualizzazione</h6>
            """   
            ),
            Div(
                'theme',
                '_dashboard_options',
                css_class="pl-lg-4"
            )
        )
        
class HospitalSelectForm(forms.Form):
    from triage.models import Hospital
    hospital = forms.ModelChoiceField(
        label=_("Ospedale"),
        queryset=Hospital.objects.all(),
        required=True,
        help_text=_("Seleziona una struttura tra quelle disponibili.")
        )
    ## Crispy forms helper for formatting staff
    helper = FormHelper()
    def __init__(self, *args,queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is not None:
            self.fields["hospital"].queryset = queryset


class HospitalEditForm(forms.ModelForm):
    class Meta:
        from triage.models import Hospital
        model = Hospital
        exclude = ("id",)
        labels = {
            "name":"Nome",
            "full_address":"Indirizzo",
            "city":"Città",
            "province":"Provincia",
            "country":"Stato",
        }
        
    ## Crispy forms helper for formatting staff
    helper = FormHelper()
    def __init__(self, *args,**kwargs):
        super().__init__(*args, **kwargs)
        
# class AccessForm(forms.ModelForm):
#     class Meta:
#         from triage.models import TriageAccess
#         model = TriageAccess
#         exclude = ("id",)
#         labels = {
#             "patient":"Paziente",
#             "hospital":"Ospedale",
#             "totem":"Totem",
#             "triage_code": "Codice Triage",
#             "access_reason":"Ragione di accesso",
#             "access_date":"Data di accesso",
#             "exit_date":"Data di uscita"
#         }
    
#     ## Crispy forms helper for formatting staff
#     helper = FormHelper()
    
#     def __init__(self, *args, readonly=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         for visible in self.visible_fields():
#             if isinstance(visible.field,forms.DateField):
#                 visible.field.widget.input_type = "date"
#         if readonly is not None:
#             for field in self:
#                 field.field.disabled = True