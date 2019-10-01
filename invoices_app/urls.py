from django.conf.urls import url

from invoices_app.views import (
    InvoiceListView,
    InvoiceUpdateView,
    SupplierInvoiceListView,
    SupplierInvoiceCreateView
)

urlpatterns = [
    url(r'^$', InvoiceListView.as_view(), name='invoices-list'),
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/$', SupplierInvoiceListView.as_view(), name='supplier-invoice-list'),
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/new/$', SupplierInvoiceCreateView.as_view(), name='invoice-create'),
    url(
        r'^taxpayer/(?P<taxpayer_id>[0-9]+)/update/(?P<pk>[0-9]+)/$',
        InvoiceUpdateView.as_view(),
        name='taxpayer-invoice-update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update$', InvoiceUpdateView.as_view(), name='invoice-update'
    ),
]
