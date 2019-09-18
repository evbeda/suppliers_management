# python puro

# terceros
from django.conf.urls import url
# propias

# proyecto
from .views import SupplierHome

urlpatterns = [
    url(r'^home$', SupplierHome.as_view(), name='supplier-home')
]
