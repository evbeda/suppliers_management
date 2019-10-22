from collections import namedtuple

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DBTuple = namedtuple('DBTuple', 'value verbose_name')

# 25 * 1014 * 1024
TAXPAYER_BANK_ACCOUNT_MAX_SIZE_FILE = 26214400

TAXPAYER_BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS = ['.pdf']

TAXPAYER_STATUS_ACTIVE = "APPROVED"
TAXPAYER_STATUS_CHANGE_REQUIRED = "CHANGE REQUIRED"
TAXPAYER_STATUS_PENDING = "PENDING"
TAXPAYER_STATUS_DENIED = "DENIED"

TAXPAYER_STATUS = {
    "Approved": DBTuple(TAXPAYER_STATUS_ACTIVE, _("Approved")),
    "Change required": DBTuple(TAXPAYER_STATUS_CHANGE_REQUIRED, _("Change required")),
    "Pending": DBTuple(TAXPAYER_STATUS_PENDING, _("Pending")),
    "Denied": DBTuple(TAXPAYER_STATUS_DENIED, _("Denied")),
}

PAYMENT_TERMS = [
    DBTuple(15, _("15 days")),
    DBTuple(30, _("30 days")),
]

PAYMENT_TYPES = [
    DBTuple("BANK", _("Bank")),
]

email_notifications = {
    'company_invitation': {
        'subject': 'You have been invited to BriteSu',
        'body': {
            'upper_text': (
                'Welcome to BriteSu!\n'
                'Please click on the following link to register.\n'
            ),
            'lower_text': 'Thank you!',
            'btn_text': 'Join',
            'btn_url': settings.COMPANY_INVITATION_URL,
        },
    },
    'taxpayer_approval': {
        'subject': 'Your taxpayer has been approved',
        'body': {
            'upper_text': (
                'You are ready to start using BriteSu.\n'
                'You can access the platform now and upload your invoices.\n'
            ),
            'lower_text': 'Thank you!',
            'btn_text': 'Go to BriteSu',
            'btn_url': settings.SUPPLIER_HOME_URL,
        },
    },
    'taxpayer_change_required': {
        'subject': 'Your taxpayer has some pending modifications',
        'body': {
            'upper_text': (
                'Please visit your taxpayer and read comments.\n'
                'Once changes are done and approved by eventbrite,\n'
                'we will send you an email.\n'
            ),
            'lower_text': 'Thank you!',
            'btn_text': 'Go to BriteSu',
            'btn_url': settings.SUPPLIER_HOME_URL,
        },
    },
    'taxpayer_denial': {
        'subject': 'Your taxpayer has been rejected',
        'body': {
            'upper_text': (
                'We are afraid that the taxpayer you were trying to submit is invalid\n'
                'Please contact the eventbrite employee that hired you.\n'
            ),
            'lower_text': 'Please contact the eventbrite employee that hired you, Thank you!',
            'btn_text': 'Go to BriteSu',
            'btn_url': settings.SUPPLIER_HOME_URL,
        },
    },
}


def get_taxpayer_status_choices():
    return TAXPAYER_STATUS.values()
