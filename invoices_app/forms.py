from django import forms

from django.utils.translation import gettext_lazy as _

from invoices_app import (
    INVOICE_MAX_SIZE_FILE
)
from invoices_app.models import Invoice
from utils.file_validator import validate_file


class InvoiceForm(forms.ModelForm):
    eb_entity = forms.CharField()

    class Meta:
        model = Invoice
        fields = (
            'invoice_date',
            'invoice_number',
            'po_number',
            'currency',
            'total_amount',
            'invoice_file',
            'workday_id',
        )
        widgets = {
            'currency': forms.Select(attrs={'class': 'custom-select'}),
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('e.g. 124246346')}),
            'total_amount': forms.NumberInput(
                attrs={
                    'id': 'total',
                    'class': 'form-control',
                    'placeholder': '0'
                }
            ),
            'invoice_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. 124246346'),
                }
            ),
            'workday_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Workday ID')}),
        }

