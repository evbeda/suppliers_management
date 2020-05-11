from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import (
    Client,
    TestCase,
)
from django.urls import reverse

from supplier_app.tests.factory_boy import (
    CompanyFactory,
    CompanyUserPermissionFactory
)
from users_app.factory_boy import (
    UserFactory,
)
from users_app.forms import UserAdminForm

SUPPLIER_HOME = reverse('supplier-home')
AP_HOME = reverse('ap-taxpayers')
BUYER_HOME = reverse('company-list')


class TestUser(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = UserFactory(email='normal@user.com', password='foo')
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
        self.assertEqual(
            response.template_name[0],
            'registration/invalid_login.html'
        )


class TestLoginRedirect(TestCase):
    def setUp(self):
        self.client = Client()

        self.supplier_group = Group.objects.get(name='supplier')
        self.ap_group = Group.objects.get(name='ap_administrator')
        self.user_with_eb_social = UserFactory(email='nicolas@gmail.com')
        self.user_with_eb_social.groups.add(self.supplier_group)
        self.user_with_google_social = UserFactory(email='ap@eventbrite.com')
        self.user_with_google_social.groups.add(self.ap_group)
        self.user_buyer_with_google_social = UserFactory(email='buyer@eventbrite.com')
        self.buyer_group = Group.objects.get(name='buyer')
        self.user_buyer_with_google_social.groups.add(self.buyer_group)

    def test_login_fail_should_redirect_to_loginfailview(self):
        response_supplier = self.client.get(SUPPLIER_HOME, follow=True)
        response_ap = self.client.get(AP_HOME, follow=True)
        url_ap, status_code_ap = response_ap.redirect_chain[0]
        url_sup, status_code_sup = response_supplier.redirect_chain[0]
        self.assertEqual(HTTPStatus.FOUND, status_code_ap)
        self.assertEqual('/?next={}'.format(AP_HOME), url_ap)
        self.assertEqual(HTTPStatus.FOUND, status_code_sup)
        self.assertEqual('/?next={}'.format(SUPPLIER_HOME), url_sup)

    def test_login_success_with_EB_should_redirect_to_supplier(self):
        company = CompanyFactory(
            name='Eventbrite',
            description='Best event organizer platform in town'
        )
        CompanyUserPermissionFactory(
            user=self.user_with_eb_social,
            company=company
        )
        self.client.force_login(self.user_with_eb_social)
        response = self.client.get(SUPPLIER_HOME, follow=True)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(
            'supplier_app/supplier-home.html',
            response.template_name[0]
        )

    def test_login_success_with_Google_should_redirect_to_apsite(self):
        self.user_with_google_social.groups.add(Group.objects.get(name='ap_administrator'))
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(AP_HOME, follow=True)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('supplier_app/ap-taxpayers.html', response.template_name[0])

    def test_ap_site_permission_invoice_list(self):
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(
            reverse('invoices-list'),
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_ap_site_permission_taxpayers(self):
        self.user_with_google_social.groups.add(Group.objects.get(name='ap_administrator'))
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(
            reverse('ap-taxpayers'),
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_ap_site_access_denied(self):
        user = UserFactory(email='not_allowed@user.com')
        user.groups.add(self.supplier_group)
        self.client.force_login(user)
        response = self.client.get(
            reverse('ap-taxpayers'),
            follow=True,
        )
        self.assertIn(
            (
                (reverse('supplier-home'), 302)
            ),
            response.redirect_chain
            )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(
            'supplier_app/supplier-home.html',
            response.template_name,
        )

    def test_ap_authenticated_access_login_view_should_redirect_to_ap_home(self):
        self.client.force_login(self.user_with_google_social)
        response = self.client.get(
            reverse('login'),
            follow=True,
        )
        self.assertIn(AP_HOME, [red[0] for red in response.redirect_chain])

    def test_ap_authenticated_access_login_view_should_redirect_to_buyer_home(self):
        self.client.force_login(self.user_buyer_with_google_social)
        response = self.client.get(
            reverse('login'),
            follow=True,
        )
        self.assertIn(BUYER_HOME, [red[0] for red in response.redirect_chain])

    def test_supplier_authenticated_access_login_view_should_redirect_to_supplier_home(self):
        self.client.force_login(self.user_with_eb_social)
        response = self.client.get(
            reverse('login'),
            follow=True,
        )
        self.assertIn(SUPPLIER_HOME, [red[0] for red in response.redirect_chain])


class TestAdmin(TestCase):
    def setUp(self):
        self.client = Client()
        self.ap_user = UserFactory(email='ap@eventbrite.com')
        manager_group = Group.objects.get(name='ap_manager')
        self.ap_user.groups.add(manager_group)

    def test_admin_list_view(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('manage-admins')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_change_admin_group_view(self):
        self.client.force_login(self.ap_user)
        response = self.client.post(
            reverse('change-ap-permission', kwargs={'pk': self.ap_user.id}),
            {'group_name': 'ap_reporter'}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(self.ap_user.groups.filter(name='ap_reporter').exists())

    def test_admin_remove_group(self):
        self.client.force_login(self.ap_user)
        response = self.client.post(
            reverse('change-ap-permission', kwargs={'pk': self.ap_user.id}),
            {'group_name': 'ap_manager'}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.ap_user.groups.filter(name='ap_manager').exists())

    def test_change_admin_invalid_group_view(self):
        self.client.force_login(self.ap_user)
        response = self.client.post(
            reverse('change-ap-permission', kwargs={'pk': self.ap_user.id}),
            {'group_name': 'bad_group'}
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_create_ap_user_valid_email(self):
        self.client.force_login(self.ap_user)
        group = Group.objects.get(name='ap_manager')
        response = self.client.post(
            reverse('create-admin'),
            {
                'email': 'testing@eventbrite.com',
                'groups': group.id,
            },
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_ap_user_form_valid_email(self):
        self.client.force_login(self.ap_user)
        group = Group.objects.get(name='ap_manager')
        form = UserAdminForm(
            data={
                'email': 'testing@eventbrite.com',
                'groups': [group.id],
            },
        )
        self.assertTrue(form.is_valid())

    def test_create_ap_user_form_invalid_email(self):
        self.client.force_login(self.ap_user)
        group = Group.objects.get(name='ap_manager')
        form = UserAdminForm(
            data={
                'email': 'testing@test.com',
                'groups': [group.id],
            },
        )
        self.assertFalse(form.is_valid())

    def test_create_ap_user_form_invalid_group(self):
        self.client.force_login(self.ap_user)
        form = UserAdminForm(
            data={
                'email': 'testing@test.com',
                'groups': [312],
            },
        )
        self.assertFalse(form.is_valid())
