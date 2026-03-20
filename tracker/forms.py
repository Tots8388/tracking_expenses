from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):
    class Meta:
        model  = Transaction
        fields = ['amount', 'category', 'type', 'date', 'description']
        widgets = {
            'date':        forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'type':        forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional description'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return abs(amount)