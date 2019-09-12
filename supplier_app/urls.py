# python puro

# terceros
from django.conf.urls import url
# propias

# proyecto
from .views import SupplierLogin

urlpatterns = [
    url(r'^$', SupplierLogin.as_view(), name='supplier-login')
]
