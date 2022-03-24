from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Creditor


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
