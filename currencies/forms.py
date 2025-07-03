from datetime import date, timedelta
from django import forms
from django.conf import settings
from dateutil import parser


class ExchangeRateForm(forms.Form):
    base_currency_code = forms.ChoiceField(
        choices=[(code, code) for code in settings.SUPPORTED_CURRENCIES]
    )
    target_currency_code = forms.ChoiceField(
        choices=[(code, code) for code in settings.SUPPORTED_CURRENCIES]
    )
    start_date = forms.CharField(required=True)
    end_date = forms.CharField(required=True)
    
    def clean_start_date(self):
        start_date_str = self.cleaned_data['start_date']
        try:
            start_date = parser.parse(start_date_str).date()
        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid start date format")
        
        # Check if start date is not more than 2 years in the past
        max_past_date = date.today() - timedelta(days=365 * 2)
        if start_date < max_past_date:
            raise forms.ValidationError("Start date cannot be more than 2 years in the past")
        
        if start_date > date.today():
            raise forms.ValidationError("Start date cannot be in the future")
        
        return start_date
    
    def clean_end_date(self):
        end_date_str = self.cleaned_data['end_date']
        try:
            end_date = parser.parse(end_date_str).date()
        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid end date format")
        
        if end_date > date.today():
            raise forms.ValidationError("End date cannot be in the future")
        
        return end_date
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("Start date must be before end date")
        
        return cleaned_data