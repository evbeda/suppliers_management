from django.forms import CheckboxSelectMultiple, Select
from django_filters import (
    CharFilter,
    DateFromToRangeFilter,
    FilterSet,
    MultipleChoiceFilter
)
from django.utils.translation import ugettext_lazy as _

from supplier_app.constants.taxpayer_status import get_taxpayer_status_choices
from supplier_app.models import TaxPayer
from utils.custom_filters import DateRangeWidget


class TaxPayerFilter(FilterSet):
    taxpayer_state = MultipleChoiceFilter(
        choices=get_taxpayer_status_choices,
        widget=CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        label=_("Organization state")
    )
    taxpayer_date = DateFromToRangeFilter()

    country = CharFilter(
        widget=Select(
            choices=[('AR', 'Argentina'), ['BR', 'Brasil']],
            attrs={'class': 'custom-select'}
        ),
        label=_("Country")
    )

    class Meta:
        model = TaxPayer
        fields = (
            'taxpayer_state',
            'taxpayer_date',
            'country'
        )

    def get_form_class(self):
        form = super(FilterSet, self).get_form_class()
        form.base_fields['taxpayer_date'].widget = DateRangeWidget()
        return form
