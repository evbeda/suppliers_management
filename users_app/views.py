from http import HTTPStatus

from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import permission_required as permission_required_decorator
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import Group
from django.http import (
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect
from django.views.i18n import set_language
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.utils.translation import activate
from django.urls import reverse
from users_app import ALLOWED_AP_ACCOUNTS, CAN_MANAGE_APS_PERM
from users_app.models import User


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


class AdminList(PermissionRequiredMixin, ListView):
    model = User
    template_name = 'AP_app/admins-list.html'
    permission_required = CAN_MANAGE_APS_PERM

    def get_queryset(self):
        queryset = User.objects.filter(email__endswith='@eventbrite.com')
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
