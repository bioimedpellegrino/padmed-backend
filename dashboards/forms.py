
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django import forms
from crispy_forms.helper import FormHelper

class DateRangeForm(forms.Form):
    start = forms.DateField(
        label="Data inizio",
    )
    
    end = forms.DateField(
        label="Data fine",
    )
    
    helper = FormHelper()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field,forms.DateField):
                visible.field.widget.input_type = "date"
                # visible.field.widget.attrs['class'] = 'datetimepicker'