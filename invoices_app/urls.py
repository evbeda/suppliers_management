# from django.conf.urls import url

# from invoices_app.views import (
#     InvoiceDetailView,
#     InvoiceHistory,
#     InvoiceListView,
#     InvoiceUpdateView,
#     SupplierInvoiceCreateView,
#     SupplierInvoiceListView,
#     change_invoice_status,
#     post_a_comment,
#     export_to_xlsx_invoice,
#     approve_invoice
# )

# urlpatterns = [
#     url(r'^$', InvoiceListView.as_view(), name='invoices-list'),
#     url(r'^xls/$', export_to_xlsx_invoice, name='invoice-to-xls'),
#     url(r'^invoice/history/(?P<pk>[0-9]+)/$', InvoiceHistory.as_view(), name='invoice-history'),
#     url(r'^invoice/change-status/(?P<pk>[0-9]+)/$', change_invoice_status, name='change-invoice-status'),
#     url(r'^invoice/approve/(?P<pk>[0-9]+)/$', approve_invoice, name='approve-invoice'),
#     url(r'^invoice/post-comment/(?P<pk>[0-9]+)/$', post_a_comment, name='post-comment'),
#     url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/$', SupplierInvoiceListView.as_view(), name='supplier-invoice-list'),
#     url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/new/$', SupplierInvoiceCreateView.as_view(), name='invoice-create'),
#     url(
#         r'^taxpayer/(?P<taxpayer_id>[0-9]+)/update/(?P<pk>[0-9]+)/$',
#         InvoiceUpdateView.as_view(),
#         name='taxpayer-invoice-update'
#     ),
#     url(
#         r'^(?P<pk>[0-9]+)/update$', InvoiceUpdateView.as_view(), name='invoice-update'
#     ),
#     url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/detail/(?P<pk>[0-9]+)/$', InvoiceDetailView.as_view(), name='invoices-detail'),
# ]
