from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ProductPricing
from fm.models import Product


############################
#       ProductPricing
############################
class NewProductPricingForm(forms.ModelForm):
    required_css_class = 'required'
    
    class Meta:
        model = ProductPricing
        fields = ['retail_price', 'wholesale_price']
        widgets = {
            'retail_price': forms.NumberInput(attrs={'step': '0.05'}),
            'wholesale_price': forms.NumberInput(attrs={'step': '0.05'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set other fields to be required
        self.fields['retail_price'].required = True
        self.fields['wholesale_price'].required = True