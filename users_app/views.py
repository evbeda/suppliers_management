from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
from users_app import ALLOWED_AP_ACCOUNTS


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
