from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from supplier_app.bank_info import get_bank_info_choices
from supplier_app.models import (
    Address,
    BankAccount,
    Company,
    CompanyUniqueToken,
    TaxPayer,
)
from supplier_app.tests.factory_boy import (
    AddressFactory,
    BankAccountFactory,
    CompanyFactory,
    CompanyUserPermissionFactory,
    TaxPayerFactory,
    TaxPayerArgentinaFactory,
)
from users_app.factory_boy import UserFactory


class TestTaxpayerModel(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.taxpayer = TaxPayerFactory(company=self.company)

    def test_tax_payer_entity_creation(self):
        taxpayer = TaxPayerFactory(
            company=self.company,
            business_name='Eventbrite',
            workday_id='12345'
        )
        self.assertEqual(taxpayer.business_name, 'Eventbrite')
        self.assertEqual(taxpayer.workday_id, '12345')
        self.assertEqual('Eventbrite', str(taxpayer))
        self.assertEqual(TaxPayer.objects.last(), taxpayer)

    def test_taxpayer_creation_first_time_should_have_PENDING_status(self):
        self.assertEqual(self.taxpayer.taxpayer_state, "PENDING")

    def test_create_child_of_tax_payer_should_also_create_taxpayer_father(self):
        taxpayer_arg = TaxPayerArgentinaFactory(business_name='Eventbrite')
        self.assertTrue(isinstance(taxpayer_arg, TaxPayer))
        self.assertEqual(taxpayer_arg.business_name, 'Eventbrite')
        self.assertEqual(1, len(TaxPayer.objects.filter(pk=taxpayer_arg.id)))

    def test_get_taxpayer_child(self):
        taxpayer_arg = TaxPayerArgentinaFactory(company=self.company)
        taxpayer = TaxPayer.objects.get(pk=taxpayer_arg.id)
        self.assertEqual(
            taxpayer.get_taxpayer_child(),
            taxpayer_arg
        )

    def test_taxpayer_has_workday_id(self):
        self.assertTrue(self.taxpayer.has_workday_id())

    def test_taxpayer_doesnt_have_workday_id(self):
        taxpayer = TaxPayerArgentinaFactory(workday_id="")
        self.assertFalse(taxpayer.has_workday_id())


class TestAddressModel(TestCase):
    def test_address(self):
        taxpayer = TaxPayerFactory()
        address = AddressFactory(taxpayer=taxpayer)
        self.assertEqual(
            address,
            Address.objects.last()
        )
        self.assertEqual(address.taxpayer, taxpayer)


class TestBankInfoModel(TestCase):
    def test_bank_info_choices_function(self):
        bank_info_choices = get_bank_info_choices()
        self.assertEqual(type(bank_info_choices), list)
        self.assertEqual(type(bank_info_choices[0]), tuple)
        self.assertEqual(type(bank_info_choices[2][0]), int)
        self.assertEqual(type(bank_info_choices[2][1]), str)


class TestBankAccountModel(TestCase):
    def test_bank_account_creation(self):
        taxpayer = TaxPayerFactory()
        bank = BankAccountFactory(taxpayer=taxpayer)
        self.assertEqual(
            bank,
            BankAccount.objects.last()
        )
        self.assertEqual(
            bank.taxpayer,
            taxpayer
        )

    def test_data_bank_account(self):
        bank_account = BankAccountFactory(
            bank_account_number='1234567890',
        )

        self.assertEqual(
            str(bank_account),
            "Account_number:1234567890"
        )


class TestCompanyModel(TestCase):
    def test_company(self):
        company = CompanyFactory()
        self.assertEqual(
            company.name,
            Company.objects.last().name
        )
        self.assertEqual(
            company.description,
            Company.objects.last().description
        )
        self.assertEqual(
            str(company),
            Company.objects.last().name.capitalize()
        )

    def test_company_tax_payer_relationship(self):
        company = CompanyFactory()
        taxpayer = TaxPayerFactory(company=company)
        self.assertEqual(taxpayer.company.name, company.name)


class TestCompanyUserPermissionModel(TestCase):
    def test_company_user_permissions(self):
        user = UserFactory()
        company = CompanyFactory()
        company_user_permissions = CompanyUserPermissionFactory(
                user=user,
                company=company
        )
        self.assertEqual(
            company_user_permissions.user,
            user
        )
        self.assertEqual(
            company_user_permissions.company,
            company
        )


class TestCompanyUniqueToken(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.companyuniquetoken = CompanyUniqueToken(company=self.company)

    def test_company_unique_token_relationship(self):
        self.assertEqual(
            self.company,
            self.companyuniquetoken.company
        )

    def test_token_length(self):
        token = self.companyuniquetoken._token_generator()
        self.assertEqual(len(token), 64)

    def test_company_unique_token_assing_company_token(self):
        self.companyuniquetoken.assing_company_token
        self.assertTrue(self.companyuniquetoken.token)

    def test_is_token_expired_true(self):
        minutes = 6*60
        companyuniquetoken = CompanyUniqueToken(
            company=self.company,
            created_at=(timezone.now() - timedelta(minutes=minutes))
        )
        self.assertTrue(
            companyuniquetoken.is_token_expired
        )

    def test_is_token_expired_false(self):
        minutes = 4*60
        companyuniquetoken = CompanyUniqueToken(
            company=self.company,
            created_at=(timezone.now() - timedelta(minutes=minutes))
        )
        self.assertFalse(
            companyuniquetoken.is_token_expired
        )