from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


class LoginView(TemplateView):
    template_name = 'registration/login.html'


class LogoutView(LogoutView):
    pass


class ErrorLoginView(TemplateView):
    template_name = 'registration/invalid_login.html'

