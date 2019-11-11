from collections import namedtuple
from django.utils.translation import ugettext_lazy as _


DBTuple = namedtuple('DBTuple', 'value verbose_name')

TAXPAYER_STATUS_APPROVED = "APPROVED"
TAXPAYER_STATUS_CHANGE_REQUIRED = "CHANGE REQUIRED"
TAXPAYER_STATUS_PENDING = "PENDING"
TAXPAYER_STATUS_CHANGES_PENDING = "CHANGES PENDING"
TAXPAYER_STATUS_DENIED = "DENIED"

TAXPAYER_STATUS = {
    "Approved": {
        "css-class": "badge badge-success",
        "choices": DBTuple(TAXPAYER_STATUS_APPROVED, _("Approved"))
    },
    "Change Required": {
        "css-class": "badge badge-warning",
        "choices": DBTuple(TAXPAYER_STATUS_CHANGE_REQUIRED, _("Change required"))
    },
    "Pending": {
        "css-class": "badge badge-primary",
        "choices": DBTuple(TAXPAYER_STATUS_PENDING, _("Pending"))
    },
    "Denied": {
        "css-class": "badge badge-danger",
        "choices": DBTuple(TAXPAYER_STATUS_DENIED, _("Denied"))
    },
    "Changes Pending": {
        "css-class": "badge badge-primary",
        "choices": DBTuple(TAXPAYER_STATUS_CHANGES_PENDING, _("Changes pending"))
    },
}


def get_taxpayer_status_choices():
    return [value['choices'] for value in TAXPAYER_STATUS.values()]
