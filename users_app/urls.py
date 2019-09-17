from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.GeneralLoginView.as_view(), name='login'),
]
