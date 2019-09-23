# python puro

# terceros
from django.conf.urls import url
# propias

# proyecto
from .views import SupplierHome, CreateFileView
from invoices_app.views import InvoiceCreateView


urlpatterns = [
    url(r'^home$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^file/create$', CreateFileView.as_view(), name='create-cuil'),
    url(r'^invoices/new/$', InvoiceCreateView.as_view(), name='create-invoice')
]
