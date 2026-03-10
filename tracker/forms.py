# tracker/forms.py
from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model  = Transaction
        fields = ['amount', 'category', 'type', 'date', 'description']
        widgets = {
            'date':        forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'type':        forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
