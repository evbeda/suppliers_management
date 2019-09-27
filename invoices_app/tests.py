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
        self.taxpayer = {
            'name': 'Eventbrite',
            'workday_id': '12345',
        }
        self.company = {
            'name': 'Eventbrite',
            'description': 'Bringing the world together through live experiences',
        }
        self.user = {
            'email': 'pepe@pepe.com',
        }
        self.taxpayer_ar1 = {
            'name': 'Eventbrite',
            'workday_id': '12345',
            'razon_social': 'Sociedad Anonima',
            'cuit': '20-31789965-3'
        }
        self.taxpayer_ar2 = {
            'name': 'Cocacola',
            'workday_id': '67890',
            'taxpayer_state': 'PEN',
            'razon_social': 'Sociedad Anonima',
            'cuit': '30-31789965-5'
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
        company = Company.objects.create(**self.company)
        taxpayer1 = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer1.company.name, "Eventbrite")

    def test_tax_payer_entity(self):
        company = Company.objects.create(**self.company)
        taxpayer = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer.name, 'Eventbrite')
        self.assertEqual(taxpayer.workday_id, '12345')

    def test_state_when_create_tax_payer_first_time(self):
        company = Company.objects.create(**self.company)
        taxpayer = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer.taxpayer_state, "PEND")
        self.assertEqual(str(taxpayer), "Name:Eventbrite Status:PEND")

    def test_create_child_of_tax_payer(self):
        taxpayer_ar1 = TaxPayerArgentina(**self.taxpayer_ar1)
        self.assertTrue(isinstance(taxpayer_ar1, TaxPayer))
        self.assertEqual(taxpayer_ar1.name, 'Eventbrite')
        self.assertEqual(
            str(taxpayer_ar1),
            "Name:Eventbrite Status:PEND"
        )

    def test_address(self):
        company = Company.objects.create(**self.company)
        taxpayer1 = TaxPayer.objects.create(**self.taxpayer, company=company)
        address = Address(
            street='Rep. del Libano',
            number='981',
            zip_code='5501',
            city='Godoy Cruz',
            state='Mendoza',
            country='Argentina',
            taxpayer=taxpayer1
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
                taxpayer1
            )
        )
        self.assertEqual(address.taxpayer, taxpayer1)

    def test_bank_account(self):
        company = Company.objects.create(**self.company)
        taxpayer1 = TaxPayer.objects.create(**self.taxpayer, company=company)
        bank = BankAccount.objects.create(
            bank_name='Supervielle',
            bank_code='CA $',
            account_number='44-2417027-3',
            taxpayer=taxpayer1
        )
        self.assertEqual(bank.taxpayer.name, 'Eventbrite')
        self.assertEqual(str(bank), "Bank:{} bank_code:{} account_number:{}".format(
            'Supervielle',
            'CA $',
            '44-2417027-3',
        ))

    def test_get_taxpayer_childs(self):

        company = Company.objects.create(**self.company)
        TaxPayerArgentina.objects.create(**self.taxpayer_ar1, company=company)
        TaxPayerArgentina.objects.create(**self.taxpayer_ar2, company=company)
        taxpayers = TaxPayer.get_taxpayer_childs()
        self.assertEqual(
            str(taxpayers),
            '[<TaxPayerArgentina: Name:Eventbrite Status:PEND>, <TaxPayerArgentina: Name:Cocacola Status:PEN>]'
        )
