from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from users_app.models import User
from django.contrib.auth import get_user_model
from parameterized import parameterized
from django.urls import reverse
from django.utils.translation import activate


from social_core.backends.eventbrite import EventbriteOAuth2
from social_core.backends.google import GoogleOAuth2
from social_django.strategy import DjangoStrategy
from social_django.models import DjangoStorage
from social_django.models import UserSocialAuth

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


class TestLoginErrorTemplate(TestCase):
    def setup(self):
        self.client = Client()

    def test_template_login_error(self):
        # activate('en')
        response = self.client.get(reverse('login-error'))
        self.assertEqual(response.status_code, 200)


SUPPLIER_HOME = '/suppliersite/home'
AP_HOME = '/apsite/home'


class TestLoginRedirect(TestCase):
    def setUp(self):
        self.GENERIC_PASSWORD = '1234'
        self.client = Client()
        self.user_with_eb_social = \
            User.objects.create_user(email='nicolas', password=self.GENERIC_PASSWORD)
        UserSocialAuth.objects.create(
            user=self.user_with_eb_social,
            provider='eventbrite',
            uid='1233543645',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )
        self.user_with_google_social = \
            User.objects.create_user(email='pepe', password=self.GENERIC_PASSWORD)
        UserSocialAuth.objects.create(
            user=self.user_with_google_social,
            provider='google',
            uid='1233543645',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )

    def test_login_success_with_EB_should_redirect_to_suppliersite(self):
        self.client.force_login(self.user_with_eb_social)
        response = self.client.get(SUPPLIER_HOME)
        self.assertEqual(200, response.status_code)
        self.assertEqual('supplier_app/supplier-home.html', response.template_name[0])

    def test_login_fail_should_redirect_to_loginfailview(self):
        response_supplier = self.client.get(SUPPLIER_HOME, follow=True)
        response_ap = self.client.get(AP_HOME, follow=True)
        url_ap, status_code_ap = response_ap.redirect_chain[0]
        url_sup, status_code_sup = response_supplier.redirect_chain[0]
        self.assertEqual(302, status_code_ap)
        self.assertEqual('/?next={}'.format(AP_HOME), url_ap)
        self.assertEqual(302, status_code_sup)
        self.assertEqual('/?next={}'.format(SUPPLIER_HOME), url_sup)

    def test_login_success_with_Google_should_redirect_to_apsite(self):
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(AP_HOME)
        self.assertEqual(200, response.status_code)
