from django import forms
from .models import PurchaseOrder

# to override the default text field rendered by django
class DateInput(forms.DateInput):
    input_type = 'date'


class PurchaseOrderForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = PurchaseOrder
        fields = ['category', 'po_date', 'notes']
        widgets = {
            'po_date': DateInput()
        }