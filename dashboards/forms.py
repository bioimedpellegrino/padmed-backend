from django import forms
from crispy_forms.helper import FormHelper
from django.contrib.admin.widgets import AdminDateWidget

class DateRangeForm(forms.Form):
    start = forms.DateField(
        # input_formats=["%d/%m/%Y",],
        label="Data inizio",
        # widget=AdminDateWidget(),
    )
    
    end = forms.DateField(
        # input_formats=["%d/%m/%Y",],
        label="Data fine",
        # widget=AdminDateWidget(),
    )
    
    helper = FormHelper()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field,forms.DateField):
                visible.field.widget.input_type = "date"
                # visible.field.widget.attrs['class'] = 'datetimepicker'