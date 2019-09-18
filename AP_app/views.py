from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class APHome(LoginRequiredMixin, TemplateView):
    template_name = 'AP_app/ap-home.html'
    login_url = '/'
