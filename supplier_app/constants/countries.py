from collections import namedtuple
from django.utils.translation import ugettext_lazy as _

DBTuple = namedtuple('DBTuple', 'value verbose_name')

COUNTRIES = {
    "AR": DBTuple("AR", _("Argentina")),
    "BR": DBTuple("BR", _("Brazil")),
    "US": DBTuple("US", _("United states")),
}


def get_countries_choices():
    return [(country.value, country.verbose_name) for country in COUNTRIES.values()]
