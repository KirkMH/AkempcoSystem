from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from .models import PurchaseOrder, PO_Product
from fm.models import Product, Supplier

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


class PO_ProductForm(BSModalModelForm):
    required_css_class = 'required'

    class Meta:
        model = PO_Product
        fields = ['product', 'ordered_quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'size': 5}),
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = None

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'product',
            Row(
                Column('ordered_quantity', css_class='form-group col-md-6'),
                Column('unit_price', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            # Submit()
        )