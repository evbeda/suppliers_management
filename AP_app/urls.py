from django.conf.urls import url

from .views import APHome

urlpatterns = [
    url(r'^home$', APHome.as_view(), name='ap-home'),
]
