from collections import namedtuple

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


CURRENT_STATUS = 1
UNUSED_STATUS = 2

DBTuple = namedtuple('DBTuple', 'value verbose_name')

# 25 * 1014 * 1024
BANK_ACCOUNT_MAX_SIZE_FILE = 26214400
BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS = ['pdf']
TAXPAYER_CERTIFICATE_MAX_SIZE_FILE = 26214400
TAXPAYER_ALLOWED_FILE_EXTENSIONS = ['pdf']

TAXPAYER_STATUS_APPROVED = "APPROVED"
TAXPAYER_STATUS_CHANGE_REQUIRED = "CHANGE REQUIRED"
TAXPAYER_STATUS_PENDING = "PENDING"
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
}

PAYMENT_TERMS = [
    DBTuple(15, _("15 days")),
    DBTuple(30, _("30 days")),
]

PAYMENT_TYPES = [
    DBTuple("BANK", _("Bank")),
]

COMPANY_INVITATION_URL = '/suppliersite/company/join'
SUPPLIER_HOME_URL = '/suppliersite/supplier'

email_notifications = {
    'company_invitation': {
        'subject': _('You have been invited to BriteSu'),
        'body': {
            'upper_text': (
                _('Welcome to BriteSu!\n'
                'Please click on the following link to register.\n')
            ),
            'lower_text': _('Thank you!'),
            'btn_text': _('Join'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, COMPANY_INVITATION_URL),
        },
    },
    'taxpayer_approval': {
        'subject': _('Your taxpayer has been approved'),
        'body': {
            'upper_text': _(
                'You are ready to start using BriteSu.\n'
                'You can access the platform now and upload your invoices.\n'
            ),
            'lower_text': _('Thank you!'),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'taxpayer_change_required': {
        'subject': _('Your taxpayer has some pending modifications'),
        'body': {
            'upper_text': _(
                'Please visit your taxpayer and read comments.\n'
                'Once changes are done and approved by Eventbrite,\n'
                'we will send you an email.\n'
            ),
            'lower_text': _('Thank you!'),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'taxpayer_denial': {
        'subject': _('Your taxpayer has been rejected'),
        'body': {
            'upper_text': _(
                'We are afraid that the taxpayer you were trying to submit is invalid\n'
                'Please contact the Eventbrite employee that hired you.\n'
            ),
            'lower_text': _('Please contact the Eventbrite employee that hired you, Thank you!'),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
}


def get_taxpayer_status_choices():
    return [value['choices'] for value in TAXPAYER_STATUS.values()]


DATE_FORMAT = _("M d, Y")
