from bootstrap_datepicker_plus import DatePickerInput
from django import forms

from invoices_app import INVOICE_MAX_SIZE_FILE
from invoices_app.models import Invoice
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
            'po_file': forms.FileInput(
                attrs={
                    'type': 'file',
                    'class': 'custom-file-input',
                    'name': 'invoice_file',
                    'id': 'inputGroupFile02',
                    'aria-describedby': 'inputGroupFileAddon01',
                    'accept': 'application/pdf',
                }
            ),
            'vat': forms.NumberInput(
                attrs={
                    'id': 'vat',
                    'class': 'form-control',
                    'placeholder': 'VAT',
                    'onChange': 'calculate_total_amount()',
                }
            ),
            'total_amount': forms.NumberInput(
                attrs={
                    'id': 'total',
                    'class': 'form-control',
                    'placeholder': 'Total'
                }
            ),
            'net_amount': forms.NumberInput(
                attrs={
                    'id': 'net_amount',
                    'class': 'form-control', 
                    'placeholder': 'Net Amount',
                    'onChange': 'calculate_total_amount()',
                    }
                ),
            'invoice_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Invoice Number'}),
        }

    def is_valid(self):
        super(InvoiceForm, self).is_valid()
        if not self.files.get('invoice_file'):
            self.add_error('invoice_file', 'No Invoice File')
            return False

        file_fields = list(self.files.keys())
        files_valids = {}

        for file_field in file_fields:
            if self.files.get(file_field):
                file_is_valid, errors = validate_file(
                    self.files[file_field],
                    INVOICE_MAX_SIZE_FILE,
                )

                files_valids[file_field] = file_is_valid

                for error in errors:
                    if not file_is_valid:
                        self.add_error(file_field, error)

        return all(list(files_valids.values()))
