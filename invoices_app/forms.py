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
            'invoice_type',
            'invoice_number',
            'po_number',
            'currency',
            'net_amount',
            'vat',
            'total_amount',
            'invoice_file',
            'workday_id',
        )
        widgets = {
            'invoice_type': forms.Select(attrs={'class': 'custom-select'}),
            'currency': forms.Select(attrs={'class': 'custom-select'}),
            'po_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('e.g. 124246346')}),
            'invoice_file': forms.FileInput(
                attrs={
                    'type': 'file',
                    'class': 'custom-file-input',
                    'name': 'invoice_file',
                    'id': 'inputGroupFile01',
                    'aria-describedby': 'inputGroupFileAddon01',
                    'accept': 'application/pdf',
                }
            ),
            'vat': forms.NumberInput(
                attrs={
                    'id': 'vat',
                    'class': 'form-control',
                    'placeholder': '0',
                    'onChange': 'calculate_total_amount()',
                }
            ),
            'total_amount': forms.NumberInput(
                attrs={
                    'id': 'total',
                    'class': 'form-control',
                    'placeholder': '0'
                }
            ),
            'net_amount': forms.NumberInput(
                attrs={
                    'id': 'net_amount',
                    'class': 'form-control',
                    'placeholder': '0',
                    'label': _('Net Amount'),
                    'onChange': 'calculate_total_amount()',
                    }
                ),
            'invoice_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. 124246346'),
                }
            ),
            'workday_id': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Workday ID')}),

        }

