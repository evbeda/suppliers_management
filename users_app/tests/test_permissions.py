from django.test import TestCase
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from utils.permissions import create_groups_and_apply_permisssions


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
