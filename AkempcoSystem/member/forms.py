from collections.abc import Mapping
from typing import Any
from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from bootstrap_modal_forms.utils import is_ajax
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import *


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
        exclude = ('total_charges', 'transaction_count', 'total_transaction_amount',
                   'total_payments', 'remaining_credit', 'payable', 'active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_number'].required = True


class UpdateCreditorForm(forms.ModelForm):
    required_css_class = 'required'
    active = forms.ChoiceField(choices=TRUE_FALSE_CHOICES,
                               initial=False, widget=forms.Select(), label=_("Is this member/creditor still active?"))

    class Meta:
        model = Creditor
        exclude = ('total_charges', 'transaction_count', 'total_transaction_amount',
                   'total_payments', 'remaining_credit', 'payable')

############################
#       CreditorPayment
############################


class NewPaymentForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = CreditorPayment
        fields = ['amount']


############################
#       Upload Form
############################
class UploadForm(forms.Form):
    required_css_class = 'required'
    payment_file = forms.FileField(
        label='CSV file to upload:',
        allow_empty_file=False,
        required=True)
