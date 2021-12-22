from django import forms
from django.utils.translation import gettext_lazy as _
from .models import UnitOfMeasure


class NewUOMForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = UnitOfMeasure
        fields = ['uom_description']

class UpdateUOMForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = UnitOfMeasure
        fields = ['uom_description', 'status']
