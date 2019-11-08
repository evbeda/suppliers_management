from http import HTTPStatus

from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import permission_required as permission_required_decorator
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import (
    Group,
    Permission,
)
from django.http import (
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.i18n import set_language
from django.views.generic import (
    CreateView,
    TemplateView,
)
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.utils.translation import activate
from django.urls import reverse
from pure_pagination.mixins import PaginationMixin
from users_app import ALLOWED_AP_ACCOUNTS, CAN_MANAGE_APS_PERM
from users_app.models import User
from users_app.forms import UserAdminForm
from utils.send_email import (
    send_email_notification,
    build_mail_html,
)
from django.conf import settings


class LoginView(TemplateView):
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated():
            if user.is_AP:
                return HttpResponseRedirect(reverse('ap-taxpayers'))
            else:
                return HttpResponseRedirect(reverse('supplier-home'))
        else:
            return super().get(request, args, kwargs)


class LogoutView(LogoutView):
    pass


class ErrorLoginView(TemplateView):
    template_name = 'registration/invalid_login.html'


class IsApUser(UserPassesTestMixin):
    login_url = 'supplier-home'

    def test_func(self):
        return self.request.user.email in ALLOWED_AP_ACCOUNTS


class AdminList(PaginationMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'AP_app/admins-list.html'
    permission_required = CAN_MANAGE_APS_PERM
    paginate_by = 10

    def get_queryset(self):
        perm = Permission.objects.get(codename='ap_role')
        queryset = User.objects.filter(
            Q(groups__permissions=perm)).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_AP'] = self.request.user.is_AP
        context['is_ap_reporter'] = self.request.user.is_AP
        context['is_ap_manager'] = self.request.user.is_AP
        return context


@permission_required_decorator(CAN_MANAGE_APS_PERM, raise_exception=True)
def change_ap_permission(request, pk):
    group_name = request.POST.get('group_name')
    user = get_object_or_404(User, id=pk)
    group = Group.objects.filter(name=group_name).first()
    if not group:
        return HttpResponseBadRequest()
    if user.groups.filter(name=group_name).exists():
        group.user_set.remove(user)
    else:
        user.groups.add(group)
    return redirect('manage-admins')


def set_user_language(request):
    if not request.POST.get('language'):
        return HttpResponseBadRequest()

    if not request.POST.get('next'):
        return HttpResponseBadRequest()

    user = User.objects.filter(id=request.user.id).first()
    if not user:
        return set_language(request)

    if user.preferred_language != request.POST['language']:
        user.preferred_language = request.POST['language']
        user.save()
        request.user.preferred_language = request.POST['language']

    response = set_language(request)

    if response.status_code == HTTPStatus.NO_CONTENT:
        return response

    activate(request.POST['language'])

    return response


class CreateAdmin(PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserAdminForm
    template_name = 'AP_app/admin_create.html'
    success_url = reverse_lazy('manage-admins')
    permission_required = CAN_MANAGE_APS_PERM

    def form_valid(self, form):
        subject = _('You have been invited to BriteSu as AP')
        upper_text = _('Please Login as AP with the link below')
        message = build_mail_html(
            'AP',
            upper_text,
            _('Thank you'),
            'AP Login',
            '{}/login/google-oauth2/?next='.format(settings.BRITESU_BASE_URL)
        )
        recipient_list = [form.cleaned_data['email']]
        send_email_notification.apply_async([subject, message, recipient_list])
        return super().form_valid(form)
