from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^suppliersite/', include('supplier_app.urls')),
    url(r'^users/', include('users_app.urls')),
    url('', include('social_django.urls', namespace='social'))
]
