
import datetime
from dateutil.relativedelta import relativedelta
from django.forms import widgets
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper

class DateRangeForm(forms.Form):
    from .models import TriageCode
    
    start = forms.DateField(
        input_formats=["%Y-%m-%d",],
        label="Data inizio",
    )
    end = forms.DateField(
        label="Data fine",
    )
    
    ## Hidden inputs
    code = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        )
    from_hours = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
        )
    to_hours = forms.FloatField(
        widget=forms.HiddenInput(),
        required=False,
        )
    start_cache = forms.DateField(
        widget=forms.HiddenInput(),
        required=False,
    )
    end_cache = forms.DateField(
        widget=forms.HiddenInput(),
        required=False,
    )
    
    ## Crispy forms helper for formatting staff
    helper = FormHelper()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field,forms.DateField):
                visible.field.widget.input_type = "date"
                # visible.field.widget.attrs['class'] = 'datetimepicker'
    
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
        fields = ['username','first_name','last_name','email','theme','_dashboard_options']
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