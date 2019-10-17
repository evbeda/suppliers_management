from django.conf.urls import url
from users_app.views import (
    AdminList,
    LoginView,
    LogoutView,
    ErrorLoginView
)

urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^login-error$', ErrorLoginView.as_view(), name='login-error'),
    url(r'^manage-admins$', AdminList.as_view(), name='manage-admins'),
    ]
