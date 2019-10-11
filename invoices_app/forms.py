from django import forms
from invoices_app.models import Invoice
from bootstrap_datepicker_plus import DatePickerInput
from invoices_app import (
    INVOICE_MAX_SIZE_FILE,
    INVOICE_FILE_FIELDS,
)
from utils.file_validator import validate_file


class InvoiceForm(forms.ModelForm):

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
            'po_file',
        )
        widgets = {
            'invoice_date': DatePickerInput(options={
                    "format": "MM/DD/YYYY",
                    # "locale": "en",
                },
                attrs={'placeholder': 'Invoice Date', }
            ),
            'invoice_type': forms.Select(attrs={'class': 'custom-select'}),
            'currency': forms.Select(attrs={'class': 'custom-select'}),
            'po_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Purchase Order'}),
            'invoice_file': forms.FileInput(attrs={'accept': 'application/pdf'}),
            'po_file': forms.FileInput(attrs={'accept': 'application/pdf'}),
            'vat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VAT'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total'}),
            'net_amount': forms.NumberInput(attrs={'class': 'form-control',  'placeholder': 'Net Amount'}),
            'invoice_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Number'}),
        }

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return valid
        for file_field in INVOICE_FILE_FIELDS:
            file_data = self.cleaned_data[file_field]
            if file_data:
                file_is_valid, msg = validate_file(
                    file_data,
                    INVOICE_MAX_SIZE_FILE,
                )
                if not file_is_valid:
                    self.add_error(file_field, msg)
                    return file_is_valid
        return valid
