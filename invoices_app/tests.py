from parameterized import parameterized
from django.test import TestCase
<<<<<<< HEAD
from .models import Address, BankAccount, Company, CompanyUserPermission, TaxPayer, TaxPayerArgentina, TaxPayerState
from users_app.models import User
=======
from datetime import date
from os import path, remove
from unittest import mock
>>>>>>> [MINOR] EDA-526: Created invoice view and template

from django.core.files import File
from .forms import InvoiceForm
from users_app.models import User

from .models import (
    Address,
    BankAccount,
    Company,
    InvoiceArg,
    TaxPayer,
    TaxPayerArgentina,
    TaxPayerState,
)


class TestModels(TestCase):
    def setUp(self):
        self.state = TaxPayerState()
        self.state.save()
        self.company1 = Company(name='Supra', description='Best catering worlwide')
        self.company1.save()
        self.tax_payer = TaxPayer(name='Eventbrite', workday_id='12345', tax_payer_state=self.state, company=self.company1)
        self.tax_payer.save()
        self.company = {
            'name': 'Eventbrite',
            'description': 'Bringing the world together through live experiences',
        }
        self.user = {
            'email': 'pepe@pepe.com',
        }
        self.tax_payer_ar = {
            'name': 'Eventbrite',
            'workday_id': '12345',
            'tax_payer_state': self.state,
            'razon_social': 'Sociedad Anonima',
            'cuit': '20-31789965-3'
        }

    def test_company(self):
        company = Company(**self.company)
        self.assertEqual(company.name, self.company['name'])
        self.assertEqual(company.description, self.company['description'])
        self.assertEqual(
            str(company),
            "Company:{} Description:{}".format(
                self.company['name'],
                self.company['description']
            )
        )

    def test_company_user_permissions(self):
        user = User.objects.create(**self.user)
        company = Company.objects.create(**self.company)
        company_user_permissions = CompanyUserPermission.objects.create(user=user, company=company)
        self.assertEqual(
            company_user_permissions.user.email,
            self.user['email']
        )
        self.assertEqual(
            company_user_permissions.company.name,
            self.company['name']
        )

    def test_company_of_tax_payer(self):
        tax_payer1 = self.tax_payer
        self.assertEqual(tax_payer1.company.name, "Supra")

    def test_tax_payer_entity(self):
        tax_payer = self.tax_payer
        self.assertEqual(tax_payer.name, 'Eventbrite')
        self.assertEqual(tax_payer.workday_id, '12345')
        self.assertEqual(tax_payer.tax_payer_state, self.state)
        self.assertEqual(str(tax_payer), tax_payer.name)

    def test_state_when_create_tax_payer_first_time(self):
        tax_payer = self.tax_payer
        self.assertEqual(tax_payer.tax_payer_state.name_tax_payer_state, "Pending")
        self.assertEqual(str(tax_payer.tax_payer_state), "Status: {}".format("Pending"))

    def test_create_child_of_tax_payer(self):
        tax_payer_ar = TaxPayerArgentina(**self.tax_payer_ar)
        self.assertTrue(isinstance(tax_payer_ar, TaxPayer))
        self.assertEqual(tax_payer_ar.name, 'Eventbrite')
        self.assertEqual(
            str(tax_payer_ar),
            "Razon Social: {} CUIT: {}".format(
                self.tax_payer_ar['razon_social'],
                self.tax_payer_ar['cuit'],
            )
        )

    def test_address(self):
        address = Address(
            street='Rep. del Libano',
            number='981',
            zip_code='5501',
            city='Godoy Cruz',
            state='Mendoza',
            country='Argentina',
            tax_payer=self.tax_payer
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
                self.tax_payer
            )
        )
        self.assertEqual(address.tax_payer, self.tax_payer)

    def test_bank_account(self):
        taxpayer = self.tax_payer
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


class TestInvoice(TestCase):
    def setUp(self):

        self.company = Company.objects.create(name='Company testing')
        self.user = User.objects.create_user(email='test_test@test.com')
        self.tax_payer = TaxPayer.objects.create(
            workday_id='4',
            name='Test',
            payment_option='Test',
            company=self.company,
            user=self.user
        )
        self.invoice_creation_valid_data = {
            'invoice_date': date(2007, 12, 5),
            'invoice_type': 'A',
            'invoice_number': '1234',
            'po_number': '98876',
            'currency': 'ARS',
            'net_amount': '4000',
            'vat': '1200',
            'total_amount': '5200',
            'invoice_file': 'test.pdf',
            'tax_payer': self.tax_payer,
        }
        self.invoice_creation_empty_data = {}
        self.file_mock = mock.MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'

    def tearDown(self):
        if path.exists(self.file_mock.name):
            remove(self.file_mock.name)

    def test_invoice_create(self):
        
        form = InvoiceForm(
            data=self.invoice_creation_valid_data,
            files={
                'invoice_file': self.file_mock,
            }
        )
        self.assertTrue(form.is_valid())

    def test_invoice_create_required_fields(self):
        form = InvoiceForm(
            data=self.invoice_creation_empty_data
        )
        self.assertFalse(form.is_valid())

    def test_invoice_create_db(self):
        invoice = InvoiceArg.objects.create(
            invoice_date=date(2007, 12, 5),
            tax_payer=self.tax_payer,
            invoice_type='A',
            invoice_number='1234',
            po_number='98876',
            currency='ARS',
            net_amount='4000',
            vat='1200',
            total_amount='5200',
            invoice_file=self.file_mock,
            user=self.user,
            )
        self.assertEqual(InvoiceArg.objects.get(invoice_number='1234'), invoice)

