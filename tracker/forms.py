from django import forms
from .models import Transaction, EmailNotificationPreference


class TransactionForm(forms.ModelForm):
    class Meta:
        model  = Transaction
        fields = ['type', 'amount', 'category', 'date', 'description', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return abs(amount)


class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model  = EmailNotificationPreference
        fields = ['weekly_summary', 'budget_alerts', 'large_expense_alert', 'large_expense_threshold']
        widgets = {
            'large_expense_threshold': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }