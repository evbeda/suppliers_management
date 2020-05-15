from django.conf import settings
from django.utils.translation import ugettext_lazy as _


COMPANY_INVITATION_URL = '/users/supplier/company/join'
SUPPLIER_HOME_URL = '/users/supplier'
HOME_URL = '/'

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
                'Instructions on next steps, '
                "First, Soon your contact at Eventbrite will send you a Purchase Order Number."
                "Then, Once you receive the Purchase Order Number, "
                "you'll need to include that on your invoice as reference."
                "Finally, send your invoice to payables-ar@eventbrite.com."
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
    'taxpayer_in_progress': {
        'subject': _('Your taxpayer is in progress now'),
        'body': {
            'upper_text': _(
                'Your taxpayer is now in progress to be approved'
            ),
            'lower_text': _("You don't need to do anything else, we will contact with you soon, Thanks!"),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'buyer_notification': {
            'subject': _('Now you can create a Purchase Requisition for this Supplier on Workday'),
            'body': {
                'upper_text': _(
                    "Once your Purchase Requisition is approved you will receive a Purchase Order Number from Workday. "
                ),
                'lower_text': _("Remember to inform the supplier of the Purchase Order Number as soon as you get it so"
                                " that the supplier can send the invoice."),
                'btn_text': _('Go to BriteSu'),
                'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, HOME_URL),
            },
        },
}
