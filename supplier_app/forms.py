from django import forms
from django.forms.models import ModelForm
from invoices_app.models import InvoiceArg
from bootstrap_datepicker_plus import DatePickerInput
from .models import PDFFile
from . import (
    MAX_SIZE_FILE,
    ALLOWED_FILE_EXTENSIONS
)

from invoices_app.models import (
    Address,
    BankAccount,
    TaxPayerArgentina,
    Company
)


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
            'invoice_date': DatePickerInput(options={
                    "format": "DD/MM/YYYY",
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


class PDFFileForm(forms.ModelForm):
    class Meta:
        model = PDFFile
        fields = ['pdf_file']
        widgets = {
            'pdf_file': forms.FileInput(attrs={'accept': 'application/pdf'}),
        }

    def is_valid(self):
        valid = super(PDFFileForm, self).is_valid()
        if not valid:
            return valid
        if self.cleaned_data['pdf_file'].size <= MAX_SIZE_FILE:
            valid_file_extensions = \
                [i for i in ALLOWED_FILE_EXTENSIONS if i in self.cleaned_data['pdf_file'].name]
            if len(valid_file_extensions) == 1:
                return True
            else:
                self.add_error(
                    'pdf_file',
                    'Your file is not a pdf'
                )
                return False

        self.add_error(
            'pdf_file',
            'Your file is greater than 3096KB.'
        )
        return False


class AddressCreateForm(ModelForm):
    prefix = 'address_form'

    class Meta:
        model = Address
        exclude = ['taxpayer']


class TaxPayerCreateForm(ModelForm):
    prefix = 'taxpayer_form'

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = self.get_user_companies(user)

    def get_user_companies(self, user):
        return Company.objects.filter(companyuserpermission__user=user)

    class Meta:
        model = TaxPayerArgentina
        exclude = ['taxpayer_state', 'workday_id']


class BankAccountCreateForm(ModelForm):
    prefix = 'bankaccount_form'

    class Meta:
        model = BankAccount
        exclude = ['taxpayer']
