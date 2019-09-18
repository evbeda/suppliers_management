from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.shortcuts import render
from django.contrib.auth.views import LoginView, TemplateView


class SupplierLoginView(TemplateView):
    template_name = 'registration/login.html'


class SupplierLogoutView(LogoutView):
    pass


class ErrorLoginView(TemplateView):
    template_name = 'registration/invalid_login.html'

