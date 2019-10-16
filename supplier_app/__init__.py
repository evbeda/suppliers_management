from collections import namedtuple

from django.conf import settings

DBTuple = namedtuple('DBTuple', 'value verbose_name')

# 25 * 1014 * 1024
TAXPAYER_BANK_ACCOUNT_MAX_SIZE_FILE = 26214400

TAXPAYER_BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS = ['.pdf']

TAXPAYER_STATUS = {
    "Active": "ACTIVE",
    "Change required": "CHANGE REQUIRED",
    "Pending": "PENDING",
    "Denied": "DENIED",
}

PAYMENT_TERMS = [
    DBTuple(15, "15 days"),
    DBTuple(30, "30 days"),
]

PAYMENT_TYPES = [
    DBTuple("BANK", "Bank"),
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
    return [(v, k) for k, v in TAXPAYER_STATUS.items()]


def get_taxpayer_status_pending_and_change_required():
    return [v for k, v in TAXPAYER_STATUS.items() if (k == "Pending" or k == "Change required")]
