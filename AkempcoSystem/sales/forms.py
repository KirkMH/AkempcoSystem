from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Creditor, SalesPayment, Sales
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


TRUE_FALSE_CHOICES = (
    (False, 'No'),
    (True, 'Yes'),
)
############################
#       Creditor
############################
class NewCreditorForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Creditor
        exclude = ['active', ]

class UpdateCreditorForm(forms.ModelForm):
    required_css_class = 'required'
    active = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Is this member/creditor still active?"))

    class Meta:
        model = Creditor
        fields = '__all__'


#####################################
###     SalesPayment - Checking out
#####################################
        
class SalesPaymentForm(BSModalModelForm):
    required_css_class = 'required'

    class Meta:
        model = SalesPayment
        fields = ['payment_mode', 'details', 'amount']

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_mode'].initial = SalesPayment.CASH

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'payment_mode',
            Row(
                Column('details', css_class='form-group col-md-12'),
                css_class='form-row'
            ),
            Row(
                Column('amount', css_class='form-group col-md-12'),
                css_class='form-row'
            ),
            # Submit()
        )


#####################################
###     Discounting - Update Sales
#####################################
class DiscountForm(BSModalModelForm):
    required_css_class = 'required'

    class Meta:
        model = Sales
        fields = ['discount_type', 'customer_name', 'customer_address', 'customer_id_card', 'customer_tin']

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'discount_type',
            Row(
                Column('customer_name', css_class='form-group col-md-6 mb-0'),
                Column('customer_address', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('customer_tin', css_class='form-group col-md-6 mb-0'),
                Column('customer_id_card', css_class='form-group col-md-6 mb-0'),
            ),
            # Submit()
        )