from django.conf.urls import url
from users_app.views import (
    AdminList,
    change_ap_permission,
    LoginView,
    LogoutView,
    ErrorLoginView,
    set_user_language,
    CreateAdmin,
)

urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^login-error$', ErrorLoginView.as_view(), name='login-error'),
    url(r'^manage-admins$', AdminList.as_view(), name='manage-admins'),
    url(r'^manage-admins/create-admin/$', CreateAdmin.as_view(), name='create-admin'),
    url(r'^manage-admins/(?P<pk>[0-9]+)/change-ap-permission$', change_ap_permission, name='change-ap-permission'),
    url(r'^set_user_language/$', set_user_language, name='set_user_language'),
    ]
