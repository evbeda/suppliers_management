from django.forms import CheckboxSelectMultiple, Select
from django_filters import (
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    MultipleChoiceFilter
)

from supplier_app import get_taxpayer_status_choices
from supplier_app.models import TaxPayer
from utils.custom_filters import DateRangeWidget


class TaxPayerFilter(FilterSet):
    taxpayer_state = MultipleChoiceFilter(
        choices=get_taxpayer_status_choices,
        widget=CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
    )
    taxpayer_date = DateFromToRangeFilter(widget=DateRangeWidget())

    country = CharFilter(
        widget=Select(
            choices=[('AR', 'Argentina'), ['BR', 'Brasil']],
            attrs={'class': 'custom-select'}
        ),
    )

    class Meta:
        model = TaxPayer
        fields = (
            'taxpayer_state',
            'taxpayer_date',
            'country'
        )
