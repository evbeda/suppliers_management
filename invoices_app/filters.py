from django.forms import NumberInput, Select, CheckboxSelectMultiple
from django_filters import (
    DateFromToRangeFilter,
    FilterSet,
    ModelChoiceFilter,
    MultipleChoiceFilter,
    RangeFilter,
)
from django_filters.widgets import RangeWidget, SuffixedMultiWidget

from bootstrap_datepicker_plus import DatePickerInput

from supplier_app.models import TaxPayer
from invoices_app import INVOICE_STATUS
from invoices_app.models import Invoice


class NumericRangeWidget(RangeWidget):
    template_name = 'django_filters/widgets/multiwidget.html'
    suffixes = ['min', 'max']

    def __init__(self, attrs=None):
        widgets = (
            NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min'}),
            NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max'})
        )
        super(SuffixedMultiWidget, self).__init__(widgets, attrs)


class DateRangeWidget(RangeWidget):
    template_name = 'django_filters/widgets/multiwidget.html'
    suffixes = ['after', 'before']

    def __init__(self, attrs=None):
        widgets = (
            DatePickerInput(options={
                    "format": "MM/DD/YYYY",
                    # "locale": "en",
                },
                attrs={'class': 'form-control', 'placeholder': 'From Date', }
            ),
            DatePickerInput(options={
                    "format": "MM/DD/YYYY",
                    # "locale": "en",
                },
                attrs={'class': 'form-control', 'placeholder': 'To Date', }
            )
        )
        super(SuffixedMultiWidget, self).__init__(widgets, attrs)


def taxpayer_qs(request):
    user = getattr(request, 'user', None)
    if not user:
        return TaxPayer.objects.none()
    elif user.is_AP:
        return TaxPayer.objects.all()
    else:
        return TaxPayer.objects.filter(
            company__companyuserpermission__user=user)


class InvoiceFilter(FilterSet):
    status = MultipleChoiceFilter(
        choices=INVOICE_STATUS,
        widget=CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
    )
    invoice_date = DateFromToRangeFilter(widget=DateRangeWidget())
    total_amount = RangeFilter(widget=NumericRangeWidget())
    taxpayer = ModelChoiceFilter(
        queryset=taxpayer_qs,
        empty_label="All",
        widget=Select(attrs={'class': 'custom-select'}),
    )

    class Meta:
        model = Invoice
        fields = ('invoice_date', 'status', 'total_amount', 'taxpayer', )
