from django import forms
from django.forms.models import ModelForm
from django.http import QueryDict
from django.utils.translation import ugettext_lazy as _

from supplier_app import TAXPAYER_BANK_ACCOUNT_MAX_SIZE_FILE
from supplier_app.models import (
    Address,
    BankAccount,
    EBEntity,
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
            data_query_dict = \
                self._create_query_dict_filter_by_prefix(data) if data else {}
            files_query_dict = \
                self._create_query_dict_filter_by_prefix(files) if files else {}
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
        for data_key, data_value in generic_data.lists():
            if data_key.startswith(self.prefix):
                query_dict.setlist(data_key, data_value)
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
             'country': forms.Select(attrs={'class': 'form-control'}),
        }


class BankAccountBaseForm(ModelForm):
    class Meta:
        model = BankAccount
        fields = '__all__'
        widgets = {
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_cbu_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control btn btn-file',
            }),
            'bank_info': forms.Select(attrs={'class': 'form-control'}),
        }


class BankAccountCreateForm(BasePrefixCreateForm, BankAccountBaseForm):
    prefix = 'bankaccount_form'

    class Meta(BankAccountBaseForm.Meta):
        exclude = ['taxpayer']


class BankAccountEditForm(BankAccountBaseForm):
    bank_cbu_file = forms.FileField()

    class Meta(BankAccountBaseForm.Meta):
        exclude = [
            'taxpayer',
        ]


class TaxPayerArgentinaBaseForm(ModelForm):
    eb_entities = \
        forms.ModelMultipleChoiceField(
            widget=forms.SelectMultiple(attrs={"class": "form-control"}),
            queryset=EBEntity.objects.all(),
            label=_("Eventbrite entities to bill"),

        )

    class Meta:
        model = TaxPayerArgentina
        fields = '__all__'
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_term': forms.Select(attrs={'class': 'form-control'}),
            'afip_registration_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control btn btn-file',
            }),
            'witholding_taxes_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control btn btn-file',
            }),
            'taxpayer_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3'
            }),
            'workday_id': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'hidden',
                    'value': 'AR'
                })
        }


class TaxPayerCreateForm(BasePrefixCreateForm, TaxPayerArgentinaBaseForm):
    prefix = 'taxpayer_form'

    class Meta(TaxPayerArgentinaBaseForm.Meta):
        exclude = ['taxpayer_state', 'workday_id', 'company']


class TaxPayerEditForm(TaxPayerArgentinaBaseForm):
    afip_registration_file = forms.FileField()
    witholding_taxes_file = forms.FileField()

    class Meta(TaxPayerArgentinaBaseForm.Meta):
        exclude = [
            'taxpayer_state',
            'company',
            'taxpayer_comments',
            'taxpayer_date',
            ]
