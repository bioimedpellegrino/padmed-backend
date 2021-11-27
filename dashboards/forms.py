from django import forms
from crispy_forms.helper import FormHelper

class DateRangeForm(forms.Form):
    start = forms.DateField(
        input_formats="%d/%m/%Y",
        label="Data inizio"
    )
    
    end = forms.DateField(
        input_formats="%d/%m/%Y",
        label="Data fine"
    )
    
    helper = FormHelper()
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs['class'] = 'form-control'