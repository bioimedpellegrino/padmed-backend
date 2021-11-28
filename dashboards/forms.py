
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
    code = forms.ModelChoiceField(
        queryset=TriageCode.objects.all(),
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