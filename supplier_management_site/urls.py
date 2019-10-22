from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^invoices/', include('invoices_app.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^suppliersite/', include('supplier_app.urls')),
    url(r'^', include('users_app.urls')),
    url('', include('social_django.urls', namespace='social')),
]
