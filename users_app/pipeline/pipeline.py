from abc import abstractmethod

from django.contrib.auth.models import Group

from users_app import ALLOWED_AP_ACCOUNTS


def get_ap_allowed_accounts():
    return ALLOWED_AP_ACCOUNTS


def add_user_to_group(is_new, user, *args, **kwargs):
    if is_new:
        strategy = get_strategy(user.email)
        strategy.add_user_to_group(user)

    return {
            'is_new': is_new,
            'user': user
        }


def get_strategy(email):
    if email in get_ap_allowed_accounts():
        return StrategyAdminManagerGroup()

    elif email.endswith('@eventbrite.com'):
        return StrategyReporterGroup()

    else:
        return StrategySupplierGroup()


class StrategyUsersGroup():
    @abstractmethod
    def add_user_to_group(self, user):
        pass


class StrategySupplierGroup(StrategyUsersGroup):
    def add_user_to_group(self, user):
        supplier_group = Group.objects.get(name='supplier')
        user.groups.add(supplier_group)


class StrategyAdminManagerGroup(StrategyUsersGroup):
    def add_user_to_group(self, user):
        ap_admin_group = Group.objects.get(name='ap_admin')
        ap_manager_group = Group.objects.get(name='ap_manager')
        user.groups.add(ap_admin_group, ap_manager_group)


class StrategyReporterGroup(StrategyUsersGroup):
    def add_user_to_group(self, user):
        ap_reporter_group = Group.objects.get(name='ap_reporter')
        user.groups.add(ap_reporter_group)
