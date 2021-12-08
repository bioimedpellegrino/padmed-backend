
import datetime
from dateutil.relativedelta import relativedelta
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
    
    # def start_hours(self):
    #     data = self.cleaned_data.get('start', '')
    #     if data:
    #         data = data.date()
    #     return data
    
    # def end_hours(self):
    #     data = self.cleaned_data.get('end', '')
    #     if data:
    #         data = data.date()
    #     return data