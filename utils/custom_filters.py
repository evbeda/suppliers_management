from django.forms import NumberInput
from django_filters.widgets import RangeWidget, SuffixedMultiWidget
from django.utils.translation import ugettext_lazy as _

from bootstrap_datepicker_plus import DatePickerInput

from invoices_app import (
    INVOICE_DATE_FORMAT,
    ENGLISH_LANGUAGE_CODE,
)


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
                    "format": str(INVOICE_DATE_FORMAT),
                    "locale": str(ENGLISH_LANGUAGE_CODE)
                },
                attrs={'class': 'form-control', 'placeholder': _('From Date'), }
            ),
            DatePickerInput(options={
                    "format": str(INVOICE_DATE_FORMAT),
                    "locale": str(ENGLISH_LANGUAGE_CODE)
                },
                attrs={'class': 'form-control', 'placeholder': _('To Date'), }
            )
        )
        super(SuffixedMultiWidget, self).__init__(widgets, attrs)
