from django.http import HttpResponseRedirect
from django.test import TestCase

from django.contrib.auth import get_user_model
from parameterized import parameterized

from social_core.backends.eventbrite import EventbriteOAuth2
from social_core.backends.google import GoogleOAuth2
from social_django.strategy import DjangoStrategy
from social_django.models import DjangoStorage

from .validate_ap_user import allowed_email_for_admin, create_user


class TestOauth(TestCase):

    def setUp(self):
        self.strategy = DjangoStrategy(DjangoStorage())
        self.details = {
            'username': '',
            'email': '',
            'first_name': 'Test',
            'last_name': 'User',
        }
        self.kwargs = {
            'response': {
                'access_token': 'ASDFGHJKL',
                'token_type': 'bearer',
                'emails': [
                    {
                        'verified': False,
                        'primary': True
                    }
                ],
                'id': '234567854',
                'name': 'Test User',
                'first_name': 'Test',
                'last_name': 'User',
                'is_public': False,
                'image_id': None
            },
        }

    @parameterized.expand([
        ('test@email.com', False),
        ('test@eventbrite.com', True),
    ])
    def test_validate_social_auth(self, email,  expected):
        self.assertEqual(allowed_email_for_admin(email), expected)

    @parameterized.expand([
        ('test@email.com', EventbriteOAuth2()),
        ('test@eventbrite.com', GoogleOAuth2(DjangoStrategy(DjangoStorage()))),
    ])
    def test_create_user_using_oauth(self, email, backend):
        details = self.details
        details['username'] = email
        details['email'] = email
        ret = create_user(self.strategy, details, backend, None, self.kwargs)
        self.assertEqual(set(ret.keys()), set(['is_new', 'user']))

    def test_create_user_using_google_failed(self):
        backend = GoogleOAuth2(self.strategy)
        details = {
            'username': 'test@noadmin.com',
            'email': 'test@noadmin.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        ret = create_user(self.strategy, details, backend, None, self.kwargs)
        # Assert that the user is not created, can be an excepcion also
        self.assertTrue(isinstance(ret, HttpResponseRedirect))


class TestUser(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email='normal@user.com', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser('super@user.com', 'foo')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False)