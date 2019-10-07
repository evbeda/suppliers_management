from django import forms
from django.forms.models import ModelForm
from django.http import QueryDict
from supplier_app import (
    TAXPAYER_BANK_ACCOUNT_MAX_SIZE_FILE,
)

from supplier_app.models import (
    Address,
    BankAccount,
    TaxPayerArgentina,
)

from utils.file_validator import validate_file


class BasePrefixCreateForm(ModelForm):
    def __init__(self, data=None, files=None, *args, **kwargs):

        data_query_dict = None
        files_query_dict = None
        if not self.prefix:
            raise ValueError("You need to specify the prefix attribute")
        if data or files:
            data = data or {}
            files = files or {}
            data_query_dict = self._create_query_dict_filter_by_prefix(data)
            files_query_dict = self._create_query_dict_filter_by_prefix(files)

        super().__init__(
            data=data_query_dict,
            files=files_query_dict,
            *args, **kwargs)

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return valid
        file_fields = self._get_file_fields()
        if file_fields:
            for file_field in file_fields:
                if file_field not in self.cleaned_data:
                    self.add_error(file_field, 'No file')
                    return False

                file_is_valid, msg = validate_file(
                    self.cleaned_data[file_field],
                    TAXPAYER_BANK_ACCOUNT_MAX_SIZE_FILE,
                )
                if not file_is_valid:
                    self.add_error(file_field, msg)
                    return file_is_valid
            return file_is_valid
        return valid

    def _get_file_fields(self):
        return [field for field in self.fields if field.endswith('file')]

    def _create_query_dict_filter_by_prefix(self, generic_data):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(
            {
                data_key: data_value
                for data_key, data_value in generic_data.items()
                if data_key.startswith(self.prefix)
            }
        )
        return query_dict


class AddressCreateForm(BasePrefixCreateForm):
    prefix = 'address_form'

    class Meta:
        model = Address
        exclude = ['taxpayer']
        widgets = {
             'street': forms.TextInput(attrs={'class': 'form-control'}),
             'number': forms.TextInput(attrs={'class': 'form-control'}),
             'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
             'city': forms.TextInput(attrs={'class': 'form-control'}),
             'state': forms.TextInput(attrs={'class': 'form-control'}),
             'country': forms.TextInput(attrs={'class': 'form-control'}),
        }


class TaxPayerCreateForm(BasePrefixCreateForm):
    prefix = 'taxpayer_form'

    class Meta:
        model = TaxPayerArgentina
        exclude = ['taxpayer_state', 'workday_id', 'company', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3'
            }),
            'AFIP_registration_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control'
            }),
            'witholding_taxes_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control'
            }),
        }


class BankAccountCreateForm(BasePrefixCreateForm):
    prefix = 'bankaccount_form'

    class Meta:
        model = BankAccount
        exclude = ['taxpayer']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_cbu_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control'
            }),
        }


class TaxPayerEditForm(ModelForm):

    class Meta:
        model = TaxPayerArgentina
        exclude = ['taxpayer_state', 'company', 'country', 'AFIP_registration_file', 'witholding_taxes_file']
        widgets = {
            'workday_id': forms.TextInput(attrs={'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }


class BankAccountEditForm(ModelForm):
    prefix = 'bankaccount_form'

    class Meta:
        model = BankAccount
        exclude = ['taxpayer', 'bank_cbu_file']
        widgets = {
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
