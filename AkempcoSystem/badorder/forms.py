from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.utils.translation import gettext_lazy as _
from .models import *

# to override the default text field rendered by django
class DateInput(forms.DateInput):
    input_type = 'date'

############################
#       BadOrder
############################

class BadOrderForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = BadOrder
        fields = ['supplier', 'date_discovered']
        widgets = {
            'date_discovered': DateInput()
        }


############################
#       BadOrderItem
############################

class BadOrderItemForm(BSModalModelForm):
    uom = forms.CharField(label="Unit of Measure", required=False)
    stocks = forms.IntegerField(label='Remaining Stocks', required=False)
    required_css_class = 'required'

    class Meta:
        model = BadOrderItem
        fields = ['product', 'quantity', 'reason']
        widgets = {
            'product': forms.Select(attrs={'size': 5}),
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = None
        self.fields['uom'].widget.attrs['readonly'] = True
        self.fields['stocks'].widget.attrs['readonly'] = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'product',
            Row(
                Column('stocks', css_class='form-group col-md-4'),
                Column('quantity', css_class='form-group col-md-4'),
                Column('uom', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            Row(
                Column('reason', css_class='form-group col-md-12'),
                css_class='form-row'
            ),
            # Submit()
        )