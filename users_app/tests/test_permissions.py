from parameterized import parameterized

from django.test import TestCase
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from users_app.factory_boy import (
    UserFactory,
)
from utils.permissions import create_groups_and_apply_permisssions
from users_app.pipeline.pipeline import add_user_to_group


class TestUser(TestCase):

    def setUp(self):
        pass

    def test_group_creation(self):
        content_type, _ = ContentType.objects.get_or_create(app_label='users_app', model='user')
        groups = {
            'test_group': [
                ('can_test', 'test permission', content_type),
                ('can_skip_test', 'test permission', content_type),
            ],
            'other_group': [
                ('can_test_other', 'test permission', content_type),
                ('cant_skip_other_test', 'test permission', content_type),
            ],
        }
        create_groups_and_apply_permisssions(groups)

        for group in groups.keys():
            self.assertTrue(Group.objects.filter(name=group).exists())


class TestUserPermissionGroup(TestCase):
    def setUp(self):
        self.ap_admin_group = Group.objects.get(name='ap_admin')
        self.ap_manager_group = Group.objects.get(name='ap_manager')
        self.ap_reporter_group = Group.objects.get(name='ap_reporter')
        self.supplier_group = Group.objects.get(name='supplier')

    def test_add_new_AP_to_admin_and_ap_manager_group(self):
        user = UserFactory(email='nahuel.valencia@eventbrite.com')
        add_user_to_group(True, user)

        self.assertTrue((self.ap_admin_group and self.ap_manager_group) in user.groups.all())

        self.assertFalse(self.supplier_group in user.groups.all())
        self.assertFalse(self.ap_reporter_group in user.groups.all())

    def test_AP_already_in_ap_admin_and_ap_manager_group_are_not_re_assigned(self):
        user = UserFactory(email='nahuel.valencia@eventbrite.com')
        user.groups.add(self.ap_admin_group, self.ap_manager_group)

        add_user_to_group(False, user)

        self.assertTrue((self.ap_admin_group and self.ap_manager_group) in user.groups.all())
        self.assertTrue((self.supplier_group and self.ap_reporter_group) not in user.groups.all())

    def test_add_new_AP_to_ap_reporter_group(self):
        user = UserFactory(email='ap_no_in_the_list@eventbrite.com')
        add_user_to_group(True, user)

        self.assertTrue(self.ap_reporter_group in user.groups.all())

        self.assertFalse(self.ap_admin_group in user.groups.all())
        self.assertFalse(self.ap_manager_group in user.groups.all())
        self.assertFalse(self.supplier_group in user.groups.all())

    def test_AP_already_in_ap_reporter_group_are_not_re_assigned(self):
        user = UserFactory(email='ap_no_in_the_list@eventbrite.com')
        user.groups.add(self.ap_reporter_group)

        add_user_to_group(False, user)

        self.assertEqual(self.ap_reporter_group, user.groups.get())

    def test_add_new_SUPPLIER_to_a_supplier_group(self):
        user = UserFactory(email='nahuel.valencia21@gmail.com')
        add_user_to_group(True, user)

        self.assertTrue(self.supplier_group in user.groups.all())

        self.assertFalse(self.ap_admin_group in user.groups.all())
        self.assertFalse(self.ap_manager_group in user.groups.all())
        self.assertFalse(self.ap_reporter_group in user.groups.all())

    def test_SUPPLIER_already_in_a_supplier_group_are_not_re_assigned(self):
        user = UserFactory(email='nahuel.valencia21@gmail.com')
        user.groups.add(self.supplier_group)

        add_user_to_group(False, user)

        self.assertEqual(self.supplier_group, user.groups.get())
