from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from .models import RV_Product, RequisitionVoucher, StockAdjustment


class RV_ProductForm(BSModalModelForm):
    uom = forms.CharField(label="Unit of Measure", required=False)
    w_qty = forms.IntegerField(label="Warehouse Stocks", required=False)
    s_qty = forms.IntegerField(label="Store Stocks", required=False)

    required_css_class = 'required'

    class Meta:
        model = RV_Product
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'size': 5}),
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].empty_label = None
        self.fields['uom'].widget.attrs['readonly'] = True
        self.fields['w_qty'].widget.attrs['readonly'] = True
        self.fields['s_qty'].widget.attrs['readonly'] = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'product',
            Row(
                Column('s_qty', css_class='form-group col-md-6'),
                Column('w_qty', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('quantity', css_class='form-group col-md-6'),
                Column('uom', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            # Submit()
        )


class StockAdjustmentForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = StockAdjustment
        fields = ['product', 'quantity', 'location', 'reason']