from django.contrib.auth.models import Group

from users_app import ALLOWED_AP_ACCOUNTS


def add_user_to_group(is_new, user, *args, **kwargs):
    if is_new:
        if user.email in ALLOWED_AP_ACCOUNTS:
            ap_admin_group = Group.objects.get(name='ap_admin')
            ap_manager_group = Group.objects.get(name='ap_manager')
            user.groups.add(ap_admin_group, ap_manager_group)

        elif user.email.endswith('@eventbrite.com'):
            ap_reporter_group = Group.objects.get(name='ap_reporter')
            user.groups.add(ap_reporter_group)

        else:
            supplier_group = Group.objects.get(name='supplier')
            user.groups.add(supplier_group)

    return {
            'is_new': is_new,
            'user': user
        }
