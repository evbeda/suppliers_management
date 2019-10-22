from django.forms import NumberInput
from django_filters.widgets import RangeWidget, SuffixedMultiWidget
from django.utils.translation import ugettext_lazy as _

from bootstrap_datepicker_plus import DatePickerInput


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
                },
                attrs={'class': 'form-control', 'placeholder': _('From Date'), }
            ),
            DatePickerInput(options={
                    "format": "MM/DD/YYYY",
                },
                attrs={'class': 'form-control', 'placeholder': _('To Date'), }
            )
        )
        super(SuffixedMultiWidget, self).__init__(widgets, attrs)
