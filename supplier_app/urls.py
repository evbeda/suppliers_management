# python puro

# terceros
from django.conf.urls import url
# propias

# proyecto
from .views import SupplierHome, CreateFileView

urlpatterns = [
    url(r'^home$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^file/create$', CreateFileView.as_view(), name='create-cuil')
]
