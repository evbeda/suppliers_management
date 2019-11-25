from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

COMPANY_INVITATION_URL = '/users/supplier/company/join'
SUPPLIER_HOME_URL = '/users/supplier/'

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
            'btn_url':  '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
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
