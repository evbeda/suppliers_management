from django.forms import CheckboxSelectMultiple, Select
from django_filters import (
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    ModelChoiceFilter,
    MultipleChoiceFilter,
    RangeFilter
)
from django.utils.translation import ugettext_lazy as _

from invoices_app import INVOICE_STATUS
from invoices_app.models import Invoice
from supplier_app.models import TaxPayer
from users_app import CAN_VIEW_ALL_TAXPAYERS_PERM
from utils.custom_filters import (
    NumericRangeWidget,
    DateRangeWidget
)


def taxpayer_qs(request):
    user = getattr(request, 'user', None)
    if not user:
        return TaxPayer.objects.none()
    elif user.has_perm(CAN_VIEW_ALL_TAXPAYERS_PERM):
        return TaxPayer.objects.all()
    else:
        return TaxPayer.objects.filter(
            company__companyuserpermission__user=user
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
    taxpayer = ModelChoiceFilter(
        queryset=taxpayer_qs,
        empty_label=_('All'),
        widget=Select(attrs={'class': 'custom-select'}),
        label=_('Taxpayer'),
    )

    taxpayer__country = CharFilter(
        widget=Select(
            choices=[('AR', 'AR'), ('BR', 'BR'), ('US', 'US')],
            attrs={'class': 'custom-select'}
        ),
        label=_('Country'),
    )

    class Meta:
        model = Invoice
        fields = ('invoice_date', 'invoice_due_date', 'status', 'total_amount', 'taxpayer', 'taxpayer__country')

    def get_form_class(self):
        form = super(FilterSet, self).get_form_class()
        form.base_fields['invoice_date'].widget = DateRangeWidget()
        form.base_fields['invoice_due_date'].widget = DateRangeWidget()
        return form
