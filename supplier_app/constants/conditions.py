from collections import namedtuple
from django.utils.translation import ugettext_lazy as _

DBTuple = namedtuple('DBTuple', 'value verbose_name')

CONDITIONS = {
    "monotributista": DBTuple("monotributista", _("Monotributista")),
    "responsable_inscripto": DBTuple("responsable_inscripto", _("Responsable Inscripto")),
}


def get_conditions_choices():
    return [(condition.value, condition.verbose_name) for condition in CONDITIONS.values()]
