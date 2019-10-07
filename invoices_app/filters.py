from django.forms import Select
from django_filters import ChoiceFilter, DateFromToRangeFilter, FilterSet
from django_filters.widgets import SuffixedMultiWidget

from bootstrap_datepicker_plus import DatePickerInput

from invoices_app import INVOICE_STATUS
from invoices_app.models import Invoice


class CustomRangeWidget(SuffixedMultiWidget):
    template_name = 'django_filters/widgets/multiwidget.html'
    suffixes = ['min', 'max']

    def __init__(self, attrs=None):
        widgets = (
            DatePickerInput(options={
                    "format": "MM/DD/YYYY",
                    # "locale": "en",
                },
                attrs={'placeholder': 'Invoice Date', }
            ),
            DatePickerInput(options={
                    "format": "MM/DD/YYYY",
                    # "locale": "en",
                },
                attrs={'placeholder': 'Invoice Date', }
            )
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class InvoiceFilter(FilterSet):
    status = ChoiceFilter(
        choices=INVOICE_STATUS,
        empty_label="All",
        widget=Select(attrs={'class': 'custom-select'}),
    )
    invoice_date = DateFromToRangeFilter(widget=CustomRangeWidget())

    class Meta:
        model = Invoice
        fields = ('invoice_date', 'status', )
