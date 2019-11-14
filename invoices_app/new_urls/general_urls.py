from django.conf.urls import url, include

from invoices_app.views import (
    InvoiceDetailView,
    InvoiceListView,
    InvoiceUpdateView,
    SupplierInvoiceListView,
    post_a_comment,
)


invoice_pattern = [
    url(r'^$', InvoiceListView.as_view(), name='invoices-list'),
    url(r'^(?P<pk>[0-9]+)/post-comment$', post_a_comment, name='post-comment'),
    url(
        r'^(?P<pk>[0-9]+)/update$',
        InvoiceUpdateView.as_view(),
        name='invoice-update'
    ),
]

taxpayer_pattern = [
    url(r'^invoice$', SupplierInvoiceListView.as_view(), name='supplier-invoice-list'),
    url(r'^invoice/(?P<pk>[0-9]+)/$', InvoiceDetailView.as_view(), name='invoices-detail'),
    url(
        r'^update/(?P<pk>[0-9]+)/$',
        InvoiceUpdateView.as_view(),
        name='taxpayer-invoice-update'
    ),
]


urlpatterns = [
    url(r'^invoice/', include(invoice_pattern)),
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/', include(taxpayer_pattern)),
]
