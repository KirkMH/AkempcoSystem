from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *


TRUE_FALSE_CHOICES = (
    (False, 'No'),
    (True, 'Yes'),
)

############################
#       UOM
############################
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


############################
#       Category
############################

class NewCategoryForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Category
        fields = ['category_description']

class UpdateCategoryForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Category
        fields = ['category_description', 'status']
        

############################
#       Supplier
############################
        
class NewSupplierForm(forms.ModelForm):
    required_css_class = 'required'
    less_vat = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Does this supplier deducts VAT from total?"))

    class Meta:
        model = Supplier
        fields = [
            'supplier_name', 
            'address',
            'contact_person',
            'contact_info',
            'email',
            'tax_class',
            'less_vat',
            'tin',
            'notes'
        ]

class UpdateSupplierForm(forms.ModelForm):
    required_css_class = 'required'
    less_vat = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Does this supplier deducts VAT from total?"))

    class Meta:
        model = Supplier
        fields = [
            'supplier_name', 
            'address',
            'contact_person',
            'contact_info',
            'email',
            'tax_class',
            'less_vat',
            'tin',
            'notes',
            'status'
        ]
