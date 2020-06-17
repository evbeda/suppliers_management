from django.utils.translation import gettext_lazy as _

INVOICE_MAX_SIZE_FILE = 5242880

INVOICE_ALLOWED_FILE_EXTENSIONS = ['.pdf']

CURRENCIES = [
    ('ARS', 'ARS'),
    ('USD', 'USD')
    ]

INVOICE_STATUS_APPROVED = 'APPROVED'
INVOICE_STATUS_PENDING = 'PENDING'
INVOICE_STATUS_CHANGES_REQUEST = 'CHANGES REQUESTED'
INVOICE_STATUS_REJECTED = 'REJECTED'
INVOICE_STATUS_PAID = 'PAID'
INVOICE_STATUS_IN_PROGRESS = 'IN PROGRESS'

INVOICE_STATUS_APPROVED_CODE = '1'
INVOICE_STATUS_PENDING_CODE = '2'
INVOICE_STATUS_CHANGES_REQUEST_CODE = '3'
INVOICE_STATUS_REJECTED_CODE = '4'
INVOICE_STATUS_PAID_CODE = '5'
INVOICE_STATUS_IN_PROGRESS_CODE = '6'

INVOICE_STATUS = [
    (INVOICE_STATUS_APPROVED_CODE, _('APPROVED')),
    (INVOICE_STATUS_PENDING_CODE, _('PENDING')),
    (INVOICE_STATUS_CHANGES_REQUEST_CODE, _('CHANGES REQUESTED')),
    (INVOICE_STATUS_REJECTED_CODE, _('REJECTED')),
    (INVOICE_STATUS_PAID_CODE, _('PAID')),
    (INVOICE_STATUS_IN_PROGRESS_CODE, _('IN PROGRESS')),
]

INVOICE_STATUSES_DICT = {n:m for n, m in INVOICE_STATUS}

INVOICE_SHOW_ONLY_NEW_MESSAGES = [
    (1, _('Show only invoices with new messages'))
]

INVOICE_FILE_FIELDS = ['invoice_file', 'po_file']

EXPORT_TO_XLS_FULL = {
    'ID': 'pk',
    'Invoice Number': 'invoice_number',
    'Invoice Date': 'invoice_date',
    'Status': 'get_status_display',
    'Tax Payer': 'taxpayer_name',
    'Due Date': 'invoice_due_date',
    'Date Received': 'invoice_date_received',
    'Currency': 'currency',
    'Net Amount': 'net_amount',
    'VAT': 'vat',
    'Total Amount': 'total_amount',
    'Workday ID': 'workday_id'
}
EXPORT_TO_XLS_TAXPAYER = {
    'Taxpayer ID': 'pk',
    'Business name': 'business_name',
    'EB Entity to bill': 'get_eb_entity',
    'Submission Date': 'taxpayer_date',
    'Status': 'taxpayer_state',
    'Workday Id': 'workday_id',
}
INVOICE_DATE_FORMAT = _("MM/DD/YYYY")
ENGLISH_LANGUAGE_CODE = _('en')

DEFAULT_NUMBER_PAGINATION = 10
NO_WORKDAY_ID_ERROR = _("Please provide a Workday ID in order to approve an invoice")
NO_COMMENT_ERROR = _('Please add a comment to request changes')

THANK_YOU = _('Thank you,')
SINCERELY = _('Sincerely,')
EVENTBRITE_INVOICE_COMMENTED = _('Eventbrite Invoice {} commented')
NEW_COMMENT_EMAIL_TEXT = _('An Eventbrite administrator left a new comment on your Invoice #{}. Please check your '
                           'invoice on BriteSu. COMMENT: {}')
INVOICE_CHANGE_STATUS_TEXT_EMAIL = _('Invoice #{} for Eventbrite is now {}')
EVENTBRITE_INVOICE_EDITED = _('Eventbrite Invoice Edited')
INVOICE_EDIT_INVOICE_UPPER_TEXT = _('Your Invoice # {} was edited by an administrator. Please check your invoice')
INVOICE_STATUS_APPROVED_UPPER = _('Your invoice #{} for Eventbrite has been approved')
INVOICE_STATUS_APPROVED_EMAIL = _('Your invoice #{} for Eventbrite has been approved. '
                                  'We’ll let you know once it is paid.')

INVOICE_STATUS_CHANGES_REQUEST_UPPER = _('Your Invoice #{} for Eventbrite has required changes')
INVOICE_STATUS_CHANGES_REQUEST_EMAIL = _('An Eventbrite administrator has required some changes on invoice #{} '
                                         'Please check your invoice on BriteSu and apply the required changes. '
                                         'COMMENT: {}')

INVOICE_STATUS_IN_PROGRESS_EMAIL = _('Your invoice #{} is being processed by Eventbrite. We’ll let you know about its '
                                     'progress soon.')

INVOICE_STATUS_REJECTED_UPPER = _('Your invoice #{} for Eventbrite has been rejected')
INVOICE_STATUS_REJECTED_EMAIL = _('Your invoice #{} for Eventbrite has been rejected. '
                                  'Please login into BriteSu to see any additional information.')

INVOICE_STATUS_PAID_UPPER = _('Your invoice #{} for Eventbrite has been paid')
INVOICE_STATUS_PAID_EMAIL = _('Your invoice #{} for Eventbrite has been paid. '
                              'Please login into BriteSu to see any additional information.')

DISCLAIMER = _('"Please do not reply to this email. If you have any questions, please login into BriteSu and make a '
               'comment in the section related to your question."')
