from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin

from users_app import ALLOWED_AP_ACCOUNTS, CAN_MANAGE_APS_PERM
from users_app.models import User


class LoginView(TemplateView):
    template_name = 'registration/login.html'


class LogoutView(LogoutView):
    pass


class ErrorLoginView(TemplateView):
    template_name = 'registration/invalid_login.html'


class IsApUser(UserPassesTestMixin):
    login_url = 'supplier-home'

    def test_func(self):
        return self.request.user.email in ALLOWED_AP_ACCOUNTS


class AdminList(PermissionRequiredMixin, ListView):
    model = User
    template_name = 'AP_app/admins-list.html'
    permission_required = CAN_MANAGE_APS_PERM

    def get_queryset(self):
        queryset = User.objects.filter(email__endswith='@eventbrite.com')
        return queryset
