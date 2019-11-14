from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('users_app.urls')),
    url('', include('social_django.urls', namespace='social')),
]
