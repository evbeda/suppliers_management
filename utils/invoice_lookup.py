from invoices_app import INVOICE_STATUS

def invoice_status_lookup(status_value):
    value_to_return = ''
    for (key, value) in INVOICE_STATUS:
        if status_value == value:
            value_to_return = key
    return value_to_return
