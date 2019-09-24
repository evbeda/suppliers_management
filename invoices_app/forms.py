from django import forms
from .models import InvoiceArg


class InvoiceForm(forms.ModelForm):

    class Meta:
        model = InvoiceArg
        fields = (
            'invoice_date',
            'invoice_type',
            'invoice_number',
            'po_number',
            'currency',
            'net_amount',
            'vat',
            'total_amount',
            'invoice_file',
        )
        exclude = ('user', 'tax_payer', 'status')
        widgets = {
            'invoice_date': forms.DateTimeInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Date'}),
            'invoice_type': forms.Select(attrs={'class': 'custom-select'}),
            'currency': forms.Select(attrs={'class': 'custom-select'}),
            'po_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Purchase Order'}),
            'invoice_file': forms.FileInput(attrs={'accept': 'application/pdf'}),
            'vat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VAT'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total'}),
            'net_amount': forms.NumberInput(attrs={'class': 'form-control',  'placeholder': 'Net Amount'}),
            'invoice_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Number'}),

        }
