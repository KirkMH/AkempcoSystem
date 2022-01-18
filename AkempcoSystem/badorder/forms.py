from django import forms
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

class BadOrderItemForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = BadOrderItem
        exclude = ['bad_order', ]