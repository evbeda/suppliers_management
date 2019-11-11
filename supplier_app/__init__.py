from collections import namedtuple

from django.utils.translation import ugettext_lazy as _


CURRENT_STATUS = 1
UNUSED_STATUS = 2

DBTuple = namedtuple('DBTuple', 'value verbose_name')

# 25 * 1014 * 1024
BANK_ACCOUNT_MAX_SIZE_FILE = 26214400
BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS = ['pdf']
TAXPAYER_CERTIFICATE_MAX_SIZE_FILE = 26214400
TAXPAYER_ALLOWED_FILE_EXTENSIONS = ['pdf']

PAYMENT_TERMS = [
    DBTuple(15, _("15 days")),
    DBTuple(30, _("30 days")),
]

PAYMENT_TYPES = [
    DBTuple("BANK", _("Bank")),
]

DATE_FORMAT = _("M d, Y")
