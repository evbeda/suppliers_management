from django import forms
from django.forms.models import ModelForm
from django.http import QueryDict
from django.utils.translation import ugettext_lazy as _

from supplier_app.models import (
    Address,
    BankAccount,
    EBEntity,
    TaxPayerArgentina,
    ContactInformation,
)


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
            'street': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. Adolfo sourdeaux'),
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. Tigre')
                }
            ),
            'state': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. Buenos aires')
                }
            ),
            'country': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ContactInformationCreateForm(BasePrefixCreateForm):
    prefix = 'contact_form'

    class Meta:
        model = ContactInformation
        exclude = ['address', 'taxpayer']
        widgets = {
            'contact_person': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. Jhon Smith'),
                }
            ),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. jhonsmith@mail.com')
                }
            ),
            'website': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': _('e.g. www.website.com')
                }
            ),
        }


class BankAccountBaseForm(ModelForm):
    class Meta:
        model = BankAccount
        fields = '__all__'
        widgets = {
            'bank_account_number': forms.TextInput(attrs={'class': 'form-control', 'minlength': '22', 'maxlength': '22'}),
            'bank_cbu_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': '',
            }),
            'bank_info': forms.Select(attrs={'class': 'form-control'}),
            'bank_transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'bank_account_type': forms.Select(attrs={'class': 'form-control'}),
            'bank_beneficiary': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BankAccountCreateForm(BasePrefixCreateForm, BankAccountBaseForm):
    prefix = 'bank_account_form'

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
            widget=forms.CheckboxSelectMultiple(attrs={"class": ""}),
            queryset=EBEntity.objects.all(),
            label=_("Eventbrite entities to bill"),

        )

    class Meta:
        model = TaxPayerArgentina
        fields = '__all__'
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Name'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control', 'minlength': '11', 'maxlength': '12'}),
            'payment_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_term': forms.Select(attrs={'class': 'form-control'}),
            'taxpayer_condition':  forms.Select(attrs={'class': 'form-control'}),
            'afip_registration_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': '',
            }),
            'witholding_taxes_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': '',
            }),
            'witholding_suss_file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': '',
            }),
            'workday_id': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'type': 'hidden',
                    'value': 'AR'
                }),
        }


class TaxPayerCreateForm(BasePrefixCreateForm, TaxPayerArgentinaBaseForm):
    prefix = 'taxpayer_form'

    class Meta(TaxPayerArgentinaBaseForm.Meta):
        exclude = ['taxpayer_state', 'workday_id', 'company']


class TaxPayerEditForm(TaxPayerArgentinaBaseForm):
    afip_registration_file = forms.FileField()
    witholding_taxes_file = forms.FileField(required=False)

    class Meta(TaxPayerArgentinaBaseForm.Meta):
        exclude = [
            'taxpayer_state',
            'company',
            'taxpayer_date',
            'workday_id',
            ]
