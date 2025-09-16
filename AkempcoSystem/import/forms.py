from django import forms
from django.core.exceptions import ValidationError
import os

class ImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Please upload a CSV file only.',
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'form-control'
        })
    )
    # RESET_CHOICES = [
    #     (False, 'No'),
    #     (True, 'Yes')
    # ]
    # reset_data = forms.ChoiceField(
    #     label='Reset Data',
    #     help_text='Select Yes to reset the data before importing.',
    #     required=True,
    #     choices=RESET_CHOICES,
    #     initial=False,
    #     widget=forms.Select(attrs={
    #         'class': 'form-select'
    #     })
    # )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            # Check file extension
            ext = os.path.splitext(csv_file.name)[1].lower()
            if ext != '.csv':
                raise ValidationError('Only CSV files are allowed.')
            
            # Optional: Check content type as well
            content_type = csv_file.content_type
            if content_type not in ['text/csv', 'application/vnd.ms-excel', 'text/plain']:
                raise ValidationError('Invalid file type. Please upload a valid CSV file.')
            
            # Optional: Check file size (e.g., 5MB limit)
            max_size = 5 * 1024 * 1024  # 5MB
            if csv_file.size > max_size:
                raise ValidationError(f'File too large. Maximum size is {max_size/1024/1024}MB.')
                
        return csv_file
