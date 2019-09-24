from parameterized import parameterized
from django.test import TestCase
from .models import Company, BankAccount, TaxPayer, TaxPayerState, TaxPayerArgentina, Address


class TestModels(TestCase):
    def setUp(self):
        self.state = TaxPayerState()
        self.state.save()
        self.company1 = Company(name='Supra', description='Best catering worlwide')
        self.company1.save()
        self.tax_payer = TaxPayer(name='Eventbrite', workday_id='12345', tax_payer_state=self.state, company=self.company1)
        self.tax_payer.save()

    @parameterized.expand([
        ('Eventbrite', 'Bringing the world together through live experiences')
    ])
    def test_company(self, name, description):
        company = Company(name=name, description=description)
        self.assertEqual(company.name, name)
        self.assertEqual(company.description, description)
        self.assertEqual(str(company), "Company:{} Description:{}".format(name, description))

    @parameterized.expand([
        ('Eventbrite', '1234')
    ])
    def test_tax_payer_entity(self, name, workday_id):
        tax_payer1 = TaxPayer(
            name=name,
            workday_id=workday_id,
            tax_payer_state=self.state,
            company=self.company1
        )
        self.assertEqual(tax_payer1.name, name)
        self.assertEqual(tax_payer1.workday_id, workday_id)
        self.assertEqual(str(tax_payer1), tax_payer1.name)

    @parameterized.expand([
        ('Eventbrite', '1234')
    ])
    def test_state_when_create_tax_payer_first_time(self, name, workday_id):
        tax_payer1 = TaxPayer(
            name=name,
            workday_id=workday_id,
            tax_payer_state=self.state,
            company=self.company1
        )
        self.assertEqual(tax_payer1.tax_payer_state.name_tax_payer_state, "Pending")
        self.assertEqual(str(tax_payer1.tax_payer_state), "Status: {}".format("Pending"))

    @parameterized.expand([
        ('Eventbrite', '1234')
    ])
    def test_company_of_tax_payer(self, name, workday_id):
        tax_payer1 = TaxPayer(
            name=name,
            workday_id=workday_id,
            tax_payer_state=self.state,
            company=self.company1
        )
        self.assertEqual(tax_payer1.company.name, "Supra")

    @parameterized.expand([
        ('Sociedad Anonima', '123456789')
    ])
    def test_create_child_of_tax_payer(self, razon_social, cuit):
        tax_payer_ar = TaxPayerArgentina(
            name='Eventbrite',
            workday_id='12345',
            tax_payer_state=self.state,
            razon_social=razon_social,
            cuit=cuit
        )
        self.assertTrue(isinstance(tax_payer_ar, TaxPayer))
        self.assertEqual(tax_payer_ar.name, 'Eventbrite')
        self.assertEqual(str(tax_payer_ar), "Razon Social: {} CUIT: {}".format(razon_social, cuit))

    @parameterized.expand([
        ('Rep. del Libano', '981', '5501', 'Godoy Cruz', 'Mendoza', 'Argentina')
    ])
    def test_address(self, street, number, zip_code, city, state, country):
        address = Address(
            street=street,
            number=number,
            zip_code=zip_code,
            city=city,
            state=state,
            country=country,
            tax_payer=self.tax_payer
        )
        self.assertEqual(str(address), "ADDRESS \n Street: {} Number: {} Zip_Code: {} City: {} State: {} Country: {}".format(street, number, zip_code, city, state, country))
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
