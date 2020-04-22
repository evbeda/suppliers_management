from os import (
    path,
)
from shutil import rmtree
from unittest.mock import (
    MagicMock,
    Mock,
)
from http import HTTPStatus
from social_core.exceptions import AuthException
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from supplier_app.tests.factory_boy import (
    AddressFactory,
    BankAccountFactory,
    CompanyFactory,
    CompanyUserPermissionFactory,
    TaxPayerArgentinaFactory,
)
from users_app.factory_boy import (
    UserFactory,
)
from users_app.pipeline.pipeline import (
    add_user_to_group,
    check_user_backend,
)

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


def in_group(group, user):
    return True if group in user.groups.all() else False


class TestUserPermissionGroup(TestCase):
    def setUp(self):
        self.ap_admin_group = Group.objects.get(name='ap_admin')
        self.ap_manager_group = Group.objects.get(name='ap_manager')
        self.ap_reporter_group = Group.objects.get(name='ap_reporter')
        self.supplier_group = Group.objects.get(name='supplier')


class TestSupplierPermissions(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(email="nahuel.valencia21@gmail.com")
        self.supplier_group = Group.objects.get(name='supplier')
        self.user.groups.add(self.supplier_group)
        self.client.force_login(self.user)

        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50

        self.company1 = CompanyFactory(
            name='FakeCompany',
            description='Best catering worldwide'
        )
        self.company_user_permission1 = CompanyUserPermissionFactory(
            company=self.company1,
            user=self.user
        )
        self.taxpayer1 = TaxPayerArgentinaFactory(
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
            company=self.company1,
        )
        self.bank_info1 = BankAccountFactory(
            taxpayer=self.taxpayer1,
            bank_cbu_file=self.file_mock
            )
        self.addres1 = AddressFactory(taxpayer=self.taxpayer1)

        self.taxpayer2 = TaxPayerArgentinaFactory()

        self.supplier_detail_url = 'supplier-details'
        self.taxpayer_update_url = 'taxpayer-update'
        self.address_update_url = 'address-update'
        self.bank_update_url = 'bank-account-update'

    def tearDown(self):
        if self.file_mock and path.exists(
            'file/{}'.format(self.file_mock.name)
        ):
            rmtree('file')

    def test_supplier_cant_access_to_another_supplier_taxpayer_details(self):
        kwargs = {
            'taxpayer_id': self.taxpayer2.id
        }
        response = self.client.get(
            reverse(
                self.supplier_detail_url,
                kwargs=kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_supplier_can_access_to_see_his_taxpayers_details(self):
        kwargs = {
            'taxpayer_id': self.taxpayer1.id
        }
        response = self.client.get(
            reverse(
                self.supplier_detail_url,
                kwargs=kwargs
            ),
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(
            "supplier_app/taxpayer-details.html",
            response.template_name,
        )

    def test_supplier_cant_access_to_edit_another_supplier_taxpayer(self):
        kwargs = {
            'taxpayer_id': self.taxpayer2.id
        }

        response = self.client.get(
            reverse(
                self.taxpayer_update_url,
                kwargs=kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_supplier_cant_access_to_edit_another_taxpayer_address_info(self):
        address2 = AddressFactory(taxpayer=self.taxpayer2)

        kwargs = {
            'taxpayer_id': self.taxpayer1.id,
            'address_id': address2.id
        }

        response = self.client.get(
            reverse(
                self.address_update_url,
                kwargs=kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_supplier_cant_access_to_edit_another_taxpayer_bank_account(self):
        bank_info2 = BankAccountFactory(taxpayer=self.taxpayer2)

        self.kwargs = {
            'taxpayer_id': self.taxpayer1.id,
            'bank_id': bank_info2.id
        }

        response = self.client.get(
            reverse(
                self.bank_update_url,
                kwargs=self.kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_check_user_backend_eventbirte_account_not_created(self):
        user = UserFactory(email='admin@eventbrite.com')
        backend = Mock()
        backend.name = 'google-oauth2'
        details = {'email': 'admin2@eventbrite.com'}
        response = Mock()
        response.hd = "eventbrite.com"
        self.assertEqual(check_user_backend(True, user, details=details, backend=backend, response=response)['user'].get_name, "admin2")

    def test_add_user_to_group_supplier(self):
        user = UserFactory(email='supplier@supplier.com')
        backend = Mock()
        backend.name = 'eventbrite'
        add_user_to_group(True, user, backend=backend)
        self.assertTrue(user.groups.filter(name='supplier').exists())

    def test_add_user_to_group_buyer(self):
        user = UserFactory(email='buyer@buyer.com')
        backend = Mock()
        backend.name = 'google-oauth2'
        add_user_to_group(True, user, backend=backend)
        self.assertTrue(user.groups.filter(name='ap_buyer').exists())
