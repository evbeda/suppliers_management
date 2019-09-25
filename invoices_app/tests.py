from django.test import TestCase
from .models import (
    Address,
    BankAccount,
    Company,
    CompanyUserPermission,
    TaxPayer,
    TaxPayerArgentina,
)
from users_app.models import User


class TestModels(TestCase):
    def setUp(self):
        self.company1 = Company.objects.create(name='Supra', description='Best catering worldwide')
        self.taxpayer = TaxPayer.objects.create(name='Eventbrite', workday_id='12345', company=self.company1)
        self.company = {
            'name': 'Eventbrite',
            'description': 'Bringing the world together through live experiences',
        }
        self.user = {
            'email': 'pepe@pepe.com',
        }
        self.taxpayer_ar = {
            'name': 'Eventbrite',
            'workday_id': '12345',
            'razon_social': 'Sociedad Anonima',
            'cuit': '20-31789965-3'
        }

    def test_company(self):
        company = Company(**self.company)
        self.assertEqual(company.name, self.company['name'])
        self.assertEqual(company.description, self.company['description'])
        self.assertEqual(
            str(company),
            "Company:{}".format(
                self.company['name']
            )
        )

    def test_company_user_permissions(self):
        user = User.objects.create(**self.user)
        company = Company.objects.create(**self.company)
        company_user_permissions = \
            CompanyUserPermission.objects.create(user=user, company=company)
        self.assertEqual(
            company_user_permissions.user.email,
            self.user['email']
        )
        self.assertEqual(
            company_user_permissions.company.name,
            self.company['name']
        )

    def test_company_of_tax_payer(self):
        taxpayer1 = self.taxpayer
        self.assertEqual(taxpayer1.company.name, "Supra")

    def test_tax_payer_entity(self):
        taxpayer = self.taxpayer
        self.assertEqual(taxpayer.name, 'Eventbrite')
        self.assertEqual(taxpayer.workday_id, '12345')

    def test_state_when_create_tax_payer_first_time(self):
        taxpayer = self.taxpayer
        self.assertEqual(taxpayer.taxpayer_state, "PEND")
        self.assertEqual(str(taxpayer), "Name:Eventbrite Status:PEND")

    def test_create_child_of_tax_payer(self):
        taxpayer_ar = TaxPayerArgentina(**self.taxpayer_ar)
        self.assertTrue(isinstance(taxpayer_ar, TaxPayer))
        self.assertEqual(taxpayer_ar.name, 'Eventbrite')
        self.assertEqual(
            str(taxpayer_ar),
            "Name:Eventbrite Status:PEND"
        )

    def test_address(self):
        address = Address(
            street='Rep. del Libano',
            number='981',
            zip_code='5501',
            city='Godoy Cruz',
            state='Mendoza',
            country='Argentina',
            taxpayer=self.taxpayer
        )
        self.assertEqual(
            str(address),
            "ADDRESS \n Street: {} Number: {} Zip_Code: {} City: {} State: {} Country: {}".format(
                'Rep. del Libano',
                '981',
                '5501',
                'Godoy Cruz',
                'Mendoza',
                'Argentina',
                self.taxpayer
            )
        )
        self.assertEqual(address.taxpayer, self.taxpayer)

    def test_bank_account(self):
        taxpayer = self.taxpayer
        bank = BankAccount.objects.create(
            bank_name='Supervielle',
            account_type='CA $',
            account_number='44-2417027-3',
            identifier='0280042780024150240076',
            taxpayer=taxpayer
        )
        self.assertEqual(bank.taxpayer.name, 'Eventbrite')
        self.assertEqual(str(bank), "Bank:{} account_type:{} account_number:{} identifier:{}".format(
            'Supervielle',
            'CA $',
            '44-2417027-3',
            '0280042780024150240076'
        ))
