from django.conf.urls import url, include

from invoices_app.views import (
    InvoiceHistory,
    change_invoice_status,
    export_to_xlsx_invoice,
)

invoice_pattern = [
    url(r'^change-status/(?P<pk>[0-9]+)/$', change_invoice_status, name='change-invoice-status'),
    url(r'^history/(?P<pk>[0-9]+)/$', InvoiceHistory.as_view(), name='invoice-history'),
    url(r'^xls/$', export_to_xlsx_invoice, name='invoice-to-xls'),
]

urlpatterns = [
    url(r'^invoice/', include(invoice_pattern))
]
