from parameterized import parameterized
from unittest.mock import (
    MagicMock,
    patch,
)
from http import HTTPStatus

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
    get_strategy,
)
from users_app.pipeline.pipeline import (
    StrategyAdminManagerGroup,
    StrategyReporterGroup,
    StrategySupplierGroup,
)

from users_app.tests import ALLOWED_AP_ACCOUNTS_FOR_TEST
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

    def test_add_user_to_group_add_new_ap_to_admin_and_manager_group(self):
        user = UserFactory(email='nahuel.valencia@eventbrite.com')

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            add_user_to_group(True, user)

        self.assertTrue(in_group(self.ap_admin_group, user))
        self.assertTrue(in_group(self.ap_manager_group, user))

        self.assertFalse(in_group(self.supplier_group, user))
        self.assertFalse(in_group(self.ap_reporter_group, user))

    def test_add_user_to_group_add_new_ap_to_reporter_group(self):
        user = UserFactory(email='ap_not_in_the_list@eventbrite.com')

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            add_user_to_group(True, user)

        self.assertTrue(in_group(self.ap_reporter_group, user))

        self.assertFalse(in_group(self.ap_admin_group, user))
        self.assertFalse(in_group(self.ap_manager_group, user))
        self.assertFalse(in_group(self.supplier_group, user))

    def test_add_user_to_group_add_new_supplier_to_a_supplier_group(self):
        user = UserFactory(email='nahuel.valencia21@gmail.com')

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            add_user_to_group(True, user)

        self.assertTrue(in_group(self.supplier_group, user))

        self.assertFalse(in_group(self.ap_admin_group, user))
        self.assertFalse(in_group(self.ap_manager_group, user))
        self.assertFalse(in_group(self.ap_reporter_group, user))

    def test_add_user_to_group_doesnt_add_ap_if_it_is_already_in_ap_admin_and_ap_manager_group(self):
        user = UserFactory(email='nahuel.valencia@eventbrite.com')
        user.groups.add(self.ap_admin_group, self.ap_manager_group)

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            add_user_to_group(False, user)

        self.assertTrue(in_group(self.ap_admin_group, user))
        self.assertTrue(in_group(self.ap_manager_group, user))

        self.assertFalse(in_group(self.supplier_group, user))
        self.assertFalse(in_group(self.ap_reporter_group, user))

    def test_add_user_to_group_doesnt_add_ap_if_it_is_already_in_ap_reporter_group(self):
        user = UserFactory(email='ap_not_in_the_list@eventbrite.com')
        user.groups.add(self.ap_reporter_group)

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            add_user_to_group(False, user)

        self.assertEqual(self.ap_reporter_group, user.groups.get())

    def test_add_user_to_group_doesnt_add_supplier_if_it_is_already_in_a_supplier_group(self):
        user = UserFactory(email='nahuel.valencia21@gmail.com')
        user.groups.add(self.supplier_group)

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            add_user_to_group(False, user)

        self.assertEqual(self.supplier_group, user.groups.get())


class TestStrategy(TestCase):
    def setUp(self):
        self.ap_admin_group = Group.objects.get(name='ap_admin')
        self.ap_manager_group = Group.objects.get(name='ap_manager')
        self.ap_reporter_group = Group.objects.get(name='ap_reporter')
        self.supplier_group = Group.objects.get(name='supplier')

    @parameterized.expand([
        ("nahuel.valencia@eventbrite.com", StrategyAdminManagerGroup),
        ("not_in_list@eventbrite.com", StrategyReporterGroup),
        ("nahuel.valencia21@gmail.com", StrategySupplierGroup),
    ])
    def test_get_strategy(self, email, strategy_class):
        user = UserFactory()
        user.email = email

        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            strategy = get_strategy(user.email)

        self.assertEqual(type(strategy), strategy_class)

    def test_add_user_to_group_in_StrategySupplierGroup_class(self):
        user = UserFactory()
        user.email = "nahuel.valencia21@gmail.com"

        strategy = StrategySupplierGroup()
        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            strategy.add_user_to_group(user)

        self.assertTrue(in_group(self.supplier_group, user))

        self.assertFalse(in_group(self.ap_admin_group, user))
        self.assertFalse(in_group(self.ap_manager_group, user))
        self.assertFalse(in_group(self.ap_reporter_group, user))

    def test_add_user_to_group_in_StrategyAdminManagerGroup_class(self):
        user = UserFactory()
        user.email = "nahuel.valencia@eventbrite.com"

        strategy = StrategyAdminManagerGroup()
        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            strategy.add_user_to_group(user)

        self.assertTrue(in_group(self.ap_admin_group, user))
        self.assertTrue(in_group(self.ap_manager_group, user))

        self.assertFalse(in_group(self.supplier_group, user))
        self.assertFalse(in_group(self.ap_reporter_group, user))

    def test_add_user_to_group_in_StrategyReporterGroup_class(self):
        user = UserFactory()
        user.email = "no_in_list@eventbrite.com"

        strategy = StrategyReporterGroup()
        with patch('users_app.pipeline.pipeline.get_ap_allowed_accounts', return_value=ALLOWED_AP_ACCOUNTS_FOR_TEST):
            strategy.add_user_to_group(user)

        self.assertTrue(in_group(self.ap_reporter_group, user))

        self.assertFalse(in_group(self.ap_admin_group, user))
        self.assertFalse(in_group(self.ap_manager_group, user))
        self.assertFalse(in_group(self.supplier_group, user))


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
        self.companyuserpermission1 = CompanyUserPermissionFactory(
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

        self.company2 = CompanyFactory(
            name='AnotherFakeCompany',
            description='Worst catering worldwide'
        )
        self.companyuserpermission2 = CompanyUserPermissionFactory(
            company=self.company2,
        )
        self.taxpayer2 = TaxPayerArgentinaFactory(
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
            company=self.company2,
        )
        self.bank_info2 = BankAccountFactory(
            taxpayer=self.taxpayer2,
            bank_cbu_file=self.file_mock
            )
        self.addres2 = AddressFactory(taxpayer=self.taxpayer2)
        self.kwargs = {
            'taxpayer_id': self.taxpayer2.id
        }

    def test_supplier_cant_access_to_another_supplier_taxpayer_details(self):
        response = self.client.get(
            reverse(
                'supplier-details',
                kwargs=self.kwargs
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
                'supplier-details',
                kwargs=kwargs
            ),
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(
            "AP_app/ap-taxpayer-details.html",
            response.template_name,
        )

    def test_supplier_cant_access_to_edit_another_supplier_taxpayer(self):
        response = self.client.get(
            reverse(
                'taxpayer-update',
                kwargs=self.kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_supplier_cant_access_to_edit_another_taxpayer_address_info(self):
        self.kwargs = {
            'taxpayer_id': self.taxpayer1.id,
            'address_id': self.addres2.id
        }

        response = self.client.get(
            reverse(
                'address-update',
                kwargs=self.kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_supplier_cant_access_to_edit_another_taxpayer_bank_account(self):
        self.kwargs = {
            'taxpayer_id': self.taxpayer1.id,
            'bank_id': self.bank_info2.id
        }

        response = self.client.get(
            reverse(
                'bank-account-update',
                kwargs=self.kwargs
            ),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
