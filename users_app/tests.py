from django.http import HttpResponseRedirect
from django.test import TestCase
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
