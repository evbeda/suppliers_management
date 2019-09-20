from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from . import ALLOWED_AP_ACCOUNTS


class APHome(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
    template_name = 'AP_app/ap-home.html'
    login_url = '/'

    def test_func(self):
        if self.request.user.is_authenticated():
            return self.request.user.email in ALLOWED_AP_ACCOUNTS
            # return self.request.user.email.endswith('@eventbrite.com')
        else:
            return False
