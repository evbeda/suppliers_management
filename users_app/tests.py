from http import HTTPStatus
from parameterized import parameterized

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from social_django.models import UserSocialAuth

from users_app.models import User

SUPPLIER_HOME = '/suppliersite/supplier'
AP_HOME = reverse('ap-taxpayers')
GENERIC_PASSWORD = '1234'


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
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='super@user.com', password='foo', is_staff=False)

    def test_string_representation(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser('super@user.com', 'foo')
        self.assertEqual(str(admin_user), 'super@user.com')


class TestLoginErrorTemplate(TestCase):
    def setUp(self):
        self.client = Client()

    def test_template_login_error(self):
        # activate('en')
        response = self.client.get(reverse('login-error'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name[0], 'registration/invalid_login.html')


class TestLoginRedirect(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_with_eb_social = \
            User.objects.create_user(email='nicolas', password=GENERIC_PASSWORD)
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
            User.objects.create_user(email='ap@eventbrite.com', password=GENERIC_PASSWORD)
        UserSocialAuth.objects.create(
            user=self.user_with_google_social,
            provider='google-oauth2',
            uid='1233543645',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )

    def test_login_success_with_EB_should_redirect_to_suppliersite(self):
        self.client.force_login(self.user_with_eb_social)
        response = self.client.get(SUPPLIER_HOME, follow=True)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('supplier_app/supplier-home.html', response.template_name[0])

    def test_login_fail_should_redirect_to_loginfailview(self):
        response_supplier = self.client.get(SUPPLIER_HOME, follow=True)
        response_ap = self.client.get(AP_HOME, follow=True)
        url_ap, status_code_ap = response_ap.redirect_chain[0]
        url_sup, status_code_sup = response_supplier.redirect_chain[0]
        self.assertEqual(HTTPStatus.FOUND, status_code_ap)
        self.assertEqual(reverse('supplier-home')+'?next={}'.format(AP_HOME), url_ap)
        self.assertEqual(HTTPStatus.FOUND, status_code_sup)
        self.assertEqual('/?next={}'.format(SUPPLIER_HOME), url_sup)

    def test_login_success_with_Google_should_redirect_to_apsite(self):
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(AP_HOME, follow=True)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('AP_app/ap-taxpayers.html', response.template_name[0])

    @parameterized.expand([
        ('invoices-list',),
        ('ap-taxpayers',),
    ])
    def test_ap_site_permission(self, page_name):
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(
            reverse(page_name),
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand([
        # ('invoices-list',),
        ('ap-taxpayers',),
    ])
    def test_ap_site_access_denied(self, page_name):
        user = User.objects.create_user(email='not_allowed@user.com')
        self.client.force_login(user)
        response = self.client.get(
            reverse(page_name),
            follow=True,
        )
        self.assertIn(
            ('/suppliersite/supplier?next={}'.format(reverse(page_name)), 302),
            response.redirect_chain
            )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, ['supplier_app/supplier-home.html'])
