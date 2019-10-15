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

CAN_VIEW_INVOICES_PERM = 'users_app.can_view_invoices'
CAN_EDIT_INVOICES_PERM = 'users_app.can_edit_invoice'
CAN_VIEW_INVOICES_HISTORY_PERM = 'users_app.can_view_invoices_history'
CAN_VIEW_SUPPLIER_INVOICES_PERM = 'users_app.can_view_supplier_invoices'
CAN_CREATE_INVOICE_PERM = 'users_app.can_create_invoice'
CAN_VIEW_ALL_TAXPAYERS_PERM = 'users_app.can_view_all_taxpayers'
CAN_VIEW_ALL_INVOICES_PERM = 'users_app.can_view_all_invoices'
CAN_CREATE_INVOICES_PERM = 'users_app.can_create_invoice'
CAN_CHANGE_INVOICE_STATUS_PERM = 'users_app.can_change_invoice_status'
