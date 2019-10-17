INVOICE_MAX_SIZE_FILE = 5242880

INVOICE_ALLOWED_FILE_EXTENSIONS = ['.pdf']

CURRENCIES = [
    ('ARS', 'ARS'),
    ('USD', 'USD')
    ]

INVOICE_STATUS_APPROVED = 'APPROVED'
INVOICE_STATUS_NEW = 'NEW'
INVOICE_STATUS_CHANGES_REQUEST = 'CHANGES REQUESTED'
INVOICE_STATUS_REJECTED = 'REJECTED'
INVOICE_STATUS_PAID = 'PAID'

INVOICE_STATUS = [
    ('1', INVOICE_STATUS_APPROVED,),
    ('2', INVOICE_STATUS_NEW,),
    ('3', INVOICE_STATUS_CHANGES_REQUEST,),
    ('4', INVOICE_STATUS_REJECTED),
    ('5', INVOICE_STATUS_PAID,),
]

ARS_INVOICE_TYPES = [
    ('A', 'A'),
    ('C', 'C'),
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
}
