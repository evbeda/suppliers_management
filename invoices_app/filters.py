from django.forms import (
    CheckboxSelectMultiple,
    Select,
    TextInput,
)
from django_filters import (
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    MultipleChoiceFilter,
    RangeFilter,
    BooleanFilter,
)
from django.utils.translation import ugettext_lazy as _

from invoices_app import INVOICE_STATUS, INVOICE_SHOW_ONLY_NEW_MESSAGES
from invoices_app.models import Invoice
from utils.custom_filters import (
    NumericRangeWidget,
    DateRangeWidget
)


class InvoiceFilter(FilterSet):
    status = MultipleChoiceFilter(
        choices=INVOICE_STATUS,
        widget=CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        label=_('Status'),
    )
    invoice_date = DateFromToRangeFilter(label=_('Invoice Date'))
    invoice_due_date = DateFromToRangeFilter(label=_('Due Date'))

    total_amount = RangeFilter(widget=NumericRangeWidget(), label=_('Total Amount'))
    taxpayer__business_name = CharFilter(
        lookup_expr='icontains',
        widget=TextInput(attrs={
            'class': 'form-control',
            "list": "taxpayers",
            }),
        label=_('Taxpayer'),
    )

    taxpayer__country = CharFilter(
        widget=Select(
            choices=[('AR', 'AR'), ('BR', 'BR'), ('US', 'US')],
            attrs={'class': 'custom-select'}
        ),
        label=_('Country'),
    )

    new_comment_from_ap = MultipleChoiceFilter(
        choices=INVOICE_SHOW_ONLY_NEW_MESSAGES,
        widget=CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        label=_('Messages'),
    )

    new_comment_from_supplier = MultipleChoiceFilter(
        choices=INVOICE_SHOW_ONLY_NEW_MESSAGES,
        widget=CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        label=_('Messages'),
    )

    class Meta:
        model = Invoice
        fields = ('new_comment_from_ap', 'new_comment_from_supplier', 'invoice_date', 'invoice_due_date', 'status', 'total_amount', 'taxpayer__business_name', 'taxpayer__country')

    def get_form_class(self):
        form = super(FilterSet, self).get_form_class()
        form.base_fields['invoice_date'].widget = DateRangeWidget()
        form.base_fields['invoice_due_date'].widget = DateRangeWidget()
        return form
