from django.forms import CheckboxSelectMultiple, Select
from django_filters import (
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    ModelChoiceFilter,
    MultipleChoiceFilter,
    RangeFilter
)

from invoices_app import INVOICE_STATUS, CAN_VIEW_ALL_TAXPAYERS_PERM
from invoices_app.models import Invoice
from supplier_app.models import TaxPayer
from utils.custom_filters import DateRangeWidget, NumericRangeWidget


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
    )
    invoice_date = DateFromToRangeFilter(widget=DateRangeWidget())
    invoice_due_date = DateFromToRangeFilter(widget=DateRangeWidget())

    total_amount = RangeFilter(widget=NumericRangeWidget())
    taxpayer = ModelChoiceFilter(
        queryset=taxpayer_qs,
        empty_label='All',
        widget=Select(attrs={'class': 'custom-select'}),
    )

    taxpayer__country = CharFilter(
        widget=Select(
            choices=[('AR', 'Argentina'), ['BR', 'Brasil']],
            attrs={'class': 'custom-select'}
        ),
    )

    class Meta:
        model = Invoice
        fields = ('invoice_date', 'invoice_due_date', 'status', 'total_amount', 'taxpayer', 'taxpayer__country')
