from django import forms
from django.utils.translation import gettext_lazy as _
from sales.models import Discount
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
#       Discount
############################
class NewDiscountForm(forms.ModelForm):
    necessity_only = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.Select,
        required=False
    )

    required_css_class = 'required'
    class Meta:
        model = Discount
        exclude = ['active']

class UpdateDiscountForm(forms.ModelForm):
    necessity_only = forms.TypedChoiceField(
        coerce=lambda x: str(x).lower() == 'true',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.Select,
        required=False
    )
    active = forms.TypedChoiceField(
        coerce=lambda x: str(x).lower() == 'true',
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.Select,
        required=False
    )
    required_css_class = 'required'
    class Meta:
        model = Discount
        fields = '__all__'


############################
#       Category
############################

class NewCategoryForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Category
        exclude = ['status']

class UpdateCategoryForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Category
        fields = '__all__'
        

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


############################
#       Product
############################


class NewProductForm(forms.ModelForm):
    for_discount = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(),
                                label=_("Basic necessity or prime commodity?"),
                                help_text=_("If yes, Senior Citizen and PWD discounts will be applied."))
    is_consignment = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Is this a consigned product?"))
    is_buyer_info_needed = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Do you need to store the buyer's information?"))
    required_css_class = 'required'
    class Meta:
        model = Product
        fields = [
            'barcode', 
            'full_description',
            'short_name',
            'category',
            'uom',
            'reorder_point',
            'ceiling_qty',
            'wholesale_qty',
            'tax_type',
            'for_discount',
            'is_consignment',
            'is_buyer_info_needed',
            'other_info'
        ]

        
class UpdateProductForm(forms.ModelForm):
    for_discount = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(),
                                label=_("Basic necessity or prime commodity?"),
                                help_text=_("If yes, Senior Citizen and PWD discounts will be applied."))
    is_consignment = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Is this a consigned product?"))
    is_buyer_info_needed = forms.ChoiceField(choices = TRUE_FALSE_CHOICES,
                                initial=False, widget=forms.Select(), label=_("Do you need to store the buyer's information?"))
    required_css_class = 'required'
    class Meta:
        model = Product
        fields = [
            'barcode', 
            'full_description',
            'short_name',
            'category',
            'uom',
            'reorder_point',
            'ceiling_qty',
            'wholesale_qty',
            'tax_type',
            'for_discount',
            'is_consignment',
            'is_buyer_info_needed',
            'other_info',
            'status'
        ]