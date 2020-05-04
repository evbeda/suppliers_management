from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from supplier_app.constants.bank_info import get_bank_info_choices
from supplier_app.constants.eb_entities_status import (
    CURRENT_STATUS,
    UNUSED_STATUS,
)
from supplier_app.models import (
    Address,
    BankAccount,
    BankAccountArgentina,
    Company,
    CompanyUniqueToken,
    TaxPayer,
    TaxpayerComment,
    TaxPayerEBEntity,
    ContactInformation,
)
from supplier_app.tests.factory_boy import (
    AddressFactory,
    BankAccountFactory,
    CompanyFactory,
    CompanyUserPermissionFactory,
    EBEntityFactory,
    TaxPayerFactory,
    TaxPayerArgentinaFactory,
    TaxPayerEBEntityFactory,
    ContactFactory,
    BankAccountArgentinaFactory
)
from users_app.factory_boy import UserFactory


class TestTaxpayerModel(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.taxpayer = TaxPayerFactory(company=self.company)
        self.taxpayer_without_eb_entities = TaxPayerArgentinaFactory()
        self.taxpayer_with_2_eb_entities = TaxPayerArgentinaFactory()
        self.taxpayer_eb_entity_1 = TaxPayerEBEntityFactory(
            taxpayer=self.taxpayer_with_2_eb_entities
        )
        self.taxpayer_eb_entity_2 = TaxPayerEBEntityFactory(
            taxpayer=self.taxpayer_with_2_eb_entities
        )
        self.eb_entity_1 = EBEntityFactory()
        self.eb_entity_2 = EBEntityFactory()

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

    def test_taxpayer_should_create_new_relation_if_eb_entity_doesnt_exists(self):
        self.taxpayer_without_eb_entities.create_if_not_exist_taxpayer_eb_entity(
            [self.eb_entity_1, self.eb_entity_2]
        )
        self.assertEqual(2, len(self.taxpayer_without_eb_entities.eb_entities))

    def test_taxpayer_with_2_eb_entity_doesnt_add_this_2_eb_entity_again(self):
        self.taxpayer_without_eb_entities.create_if_not_exist_taxpayer_eb_entity(
            [self.eb_entity_1, self.eb_entity_2]
        )
        self.taxpayer_without_eb_entities.create_if_not_exist_taxpayer_eb_entity(
            [self.eb_entity_1, self.eb_entity_2]
        )
        self.assertEqual(2, len(self.taxpayer_without_eb_entities.eb_entities))

    def test_new_eb_entities_should_be_current(self):
        self.taxpayer_without_eb_entities.create_if_not_exist_taxpayer_eb_entity(
            [self.eb_entity_1, self.eb_entity_2]
        )
        self.assertEqual(2, len(self.taxpayer_without_eb_entities.eb_entities))

    def test_taxpayer_apply_set_unused_status_should_change_2_eb_entities(self):

        taxpayer_eb_entities = \
            self.taxpayer_with_2_eb_entities.taxpayerebentity_set.all()

        self.taxpayer_with_2_eb_entities.apply_function_to_all_elems(
            taxpayer_eb_entities,
            TaxPayerEBEntity.set_unused_status,
        )
        self.assertEqual(2, len(TaxPayerEBEntity.objects.filter(status=UNUSED_STATUS)))

    def test_taxpayer_apply_set_unused_status_should_change_1_eb_entity(self):
        taxpayer_eb_entities = [self.taxpayer_with_2_eb_entities.taxpayerebentity_set.last()]

        self.taxpayer_with_2_eb_entities.apply_function_to_all_elems(
            taxpayer_eb_entities,
            TaxPayerEBEntity.set_unused_status,
        )
        self.assertEqual(1, len(TaxPayerEBEntity.objects.filter(status=UNUSED_STATUS)))

    def test_taxpayer_apply_set_current_status_should_change_2_eb_entities(self):
        taxpayer_eb_entities = self.taxpayer_with_2_eb_entities.taxpayerebentity_set.all()

        self.taxpayer_with_2_eb_entities.apply_function_to_all_elems(
            taxpayer_eb_entities,
            TaxPayerEBEntity.set_current_status,
        )
        self.assertEqual(2, len(TaxPayerEBEntity.objects.filter(status=CURRENT_STATUS)))

    def test_taxpayer_current_entities_should_be_the_selected_ones(self):
        eb_entity_selected_1 = EBEntityFactory()
        eb_entity_selected_2 = EBEntityFactory()
        eb_entities = [eb_entity_selected_1, eb_entity_selected_2]

        self.taxpayer_with_2_eb_entities.set_current_eb_entities(eb_entities)

        taxpayer_eb_entities = self.taxpayer_with_2_eb_entities.eb_entities
        self.assertEqual(2, len(taxpayer_eb_entities))
        self.assertEqual(eb_entities, taxpayer_eb_entities)

    def test_old_taxpayer_eb_entities_should_be_unused_after_update(self):
        taxpayer = TaxPayerArgentinaFactory()
        taxpayer_eb_entity_old_1 = TaxPayerEBEntityFactory(taxpayer=taxpayer)
        taxpayer_eb_entity_old_2 = TaxPayerEBEntityFactory(taxpayer=taxpayer)
        eb_entity_selected_1 = EBEntityFactory()
        eb_entity_selected_2 = EBEntityFactory()
        eb_entities = [eb_entity_selected_1, eb_entity_selected_2]

        taxpayer.set_current_eb_entities(eb_entities)

        taxpayer_eb_entity_old_1 = TaxPayerEBEntity.objects.get(pk=taxpayer_eb_entity_old_1.id)
        taxpayer_eb_entity_old_2 = TaxPayerEBEntity.objects.get(pk=taxpayer_eb_entity_old_2.id)

        self.assertEqual(str(UNUSED_STATUS), taxpayer_eb_entity_old_1.status)
        self.assertEqual(str(UNUSED_STATUS), taxpayer_eb_entity_old_2.status)


class TestAddressModel(TestCase):
    def test_address(self):
        taxpayer = TaxPayerFactory()
        address = AddressFactory(taxpayer=taxpayer)
        self.assertEqual(
            address,
            Address.objects.last()
        )
        self.assertEqual(address.taxpayer, taxpayer)


class TestContactModel(TestCase):
    def test_address(self):
        taxpayer = TaxPayerFactory()
        contact = ContactFactory(taxpayer=taxpayer)
        self.assertEqual(
            contact,
            ContactInformation.objects.last()
        )
        self.assertEqual(contact.taxpayer, taxpayer)


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


class TestBankAccountArgentinaModel(TestCase):
    def test_bank_account_creation(self):
        bank = BankAccountArgentinaFactory()
        self.assertEqual(
            bank,
            BankAccountArgentina.objects.last()
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
            company.eb_entity,
            Company.objects.last().eb_entity
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

    @patch(
        'supplier_app.models.CompanyUniqueToken._get_token_expiration_time',
        return_value=1*60
    )
    def test_is_token_expired_true(self, mocked_token_expiration_time):
        minutes = 2*60
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


class TestTaxpayerComment(TestCase):
    def setUp(self):
        self.data = {
            'taxpayer': TaxPayerFactory(),
            'user': UserFactory(),
            'message': 'please upload updated AFIP form',
        }

    def test_taxpayer_comment_persists_in_db(self):
        self.comment = TaxpayerComment.objects.create(**self.data)

        self.assertEqual(
            self.comment,
            TaxpayerComment.objects.last()
        )

    def test_taxpayer_comment_and_taxpayer_relationship(self):
        self.comment = TaxpayerComment.objects.create(**self.data)

        self.assertEqual(
            self.comment.taxpayer,
            self.data['taxpayer']
        )
