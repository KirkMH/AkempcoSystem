from django import forms
from django.utils.translation import gettext_lazy as _
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