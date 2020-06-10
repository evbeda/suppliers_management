from django.conf import settings
from django.utils.translation import ugettext_lazy as _


COMPANY_INVITATION_URL = '/users/supplier/company/join'
SUPPLIER_HOME_URL = '/users/supplier'
HOME_URL = '/'

email_notifications = {
    'company_invitation': {
        'subject': _('You’re invited to join as a supplier for Eventbrite'),
        'body': {
            'upper_text': _(
                'Welcome to BriteSu! Please click on the following link to complete the supplier registration form before doing business with Eventbrite..'),
            'second_text': _(
                'IMPORTANT:  During the registration process you’ll be required to enter the Eventbrite entity your company will bill. Please remember to select the following entity during your registration: {}'),
            'lower_text': _('Thank you!'),
            'disclaimer': _(
                '"Please do not reply to this email. If you have any questions, please click on the “Join” button, register, and then make a comment in the section related to your question."'),
            'btn_text': _('Join'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, COMPANY_INVITATION_URL),
        },
    },
    'taxpayer_approval': {
        'subject': _('Your supplier registration request has been approved'),
        'body': {
            'upper_text': _("Soon your contact at Eventbrite will send you a Purchase Order Number. Once you receive it, you'll be able to upload your invoice on BriteSu"),
            'lower_text': _('Thank you!'),
            'disclaimer': _('"Please do not reply to this email. If you have any questions, please login into Britesu and make a comment in the section related to your question."'),
            'btn_text': _('Go to BriteSu'),
            'btn_url':  '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'taxpayer_change_required': {
        'subject': _('Your supplier registration request has some pending modifications'),
        'body': {
            'upper_text': _('Please visit your taxpayer  “Edit” section and read the comments. Once changes are done and approved by Eventbrite, we will send you an email.'),
            'lower_text': _('Thank you!'),
            'disclaimer': _('"Please do not reply to this email. If you have any questions, please login into Britesu and make a comment in the section related to your question."'),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'taxpayer_denial': {
        'subject': _('Your taxpayer has been rejected'),
        'body': {
            'upper_text': _('We are afraid that the taxpayer you were trying to submit is invalid Please contact the Eventbrite employee that hired you.'),
            'lower_text': _('Please contact the Eventbrite employee that hired you, Thank you!'),
            'disclaimer': _('"Please do not reply to this email. If you have any questions, please login into Britesu and make a comment in the section related to your question."'),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'taxpayer_in_progress': {
        'subject': _('Your registration request as an Eventbrite Supplier is now in progress'),
        'body': {
            'upper_text': _('Your supplier registration request for Eventbrite is now being processed.'),
            'lower_text': _("You don't need to do anything else, we will contact with you soon, Thanks!"),
            'disclaimer': _(
                '"Please do not reply to this email. If you have any questions, please login into Britesu and make a comment in the section related to your question."'),
            'btn_text': _('Go to BriteSu'),
            'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL),
        },
    },
    'buyer_notification': {
            'subject': _('Now you can create a Purchase Requisition for this supplier on Workday.'),
            'body': {
                'upper_text': _("Now you can create a Purchase Requisition for this supplier from Workday. Once the purchase requisition is approved, you will receive a Purchase Order Number on Workday."),
                'lower_text': _("Remember to inform the supplier on the Purchase Order Number as soon as you get it so that the supplier can include it as a reference within the invoice."),
                'disclaimer': '',
                'btn_text': _('Go to BriteSu'),
                'btn_url': '{}{}'.format(settings.BRITESU_BASE_URL, HOME_URL),
            },
        },
}
