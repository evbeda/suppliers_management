from django import forms
from invoices_app.models import Invoice
from bootstrap_datepicker_plus import DatePickerInput
from supplier_app import (
    MAX_SIZE_FILE,
    ALLOWED_FILE_EXTENSIONS
)


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
        )
        exclude = ('user', 'tax_payer', 'status')
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
            'vat': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'VAT'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total'}),
            'net_amount': forms.NumberInput(attrs={'class': 'form-control',  'placeholder': 'Net Amount'}),
            'invoice_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Number'}),
        }

    def is_valid(self):
        valid = super(InvoiceForm, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data['invoice_file'].size > MAX_SIZE_FILE:
            self.add_error(
                'invoice_file',
                'Your file is greater than {}KB.'.format(MAX_SIZE_FILE)
            )
            return False

        return True
