from django import forms
from .models import EntryAdjustment

class EntryAdjustmentForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = EntryAdjustment
        fields = ['transaction_type', 'reference_num', 'adjustment_detail', 'reason']