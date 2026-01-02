from django import forms

from .models import InventoryCountReport

# to override the default text field rendered by django


class DateInput(forms.DateInput):
    input_type = 'date'


class InventoryCountReportForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = InventoryCountReport
        fields = ['description', 'inventory_date']
        widgets = {
            'inventory_date': DateInput()
        }