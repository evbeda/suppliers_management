from http import HTTPStatus
from django.test import (
    Client,
    TestCase,
)

from django.urls import (
    reverse_lazy
)

from supplier_app.factory_boy import (
    CompanyFactory,
    TaxPayerFactory
)
from supplier_app.models import (
    Company,
    CompanyUserPermission,
)
from users_app.factory_boy import UserFactory


class TestCompanyModels(TestCase):

    def test_company(self):
        company = CompanyFactory()
        self.assertEqual(
            company.name,
            Company.objects.all().last().name
        )
        self.assertEqual(
            company.description,
            Company.objects.all().last().description
        )
        self.assertEqual(
            str(company),
            Company.objects.all().last().name.capitalize()
        )

    def test_company_tax_payer_relationship(self):
        company = CompanyFactory()
        taxpayer = TaxPayerFactory(company=company)
        self.assertEqual(taxpayer.company.name, company.name)

    def test_company_user_permissions(self):
        user = UserFactory()
        company = CompanyFactory()
        company_user_permissions = CompanyUserPermission.objects.create(
                user=user,
                company=company
        )
        self.assertEqual(
            company_user_permissions.user.email,
            user.email
        )
        self.assertEqual(
            company_user_permissions.company.name,
            company.name
        )


class TestCompanySelectorView(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

    def test_valid_company_selection_and_redirection(self):
        response = self.client.post(
            reverse_lazy('company-selector'),
            {
                'company': '1',
            },
            follow=True
        )
        self.assertEqual(
            CompanyUserPermission.objects.last().company,
            self.company
        )
        self.assertEqual(
            CompanyUserPermission.objects.last().user,
            self.user
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.redirect_chain[0][0],
            '/suppliersite/supplier'
        )

    def test_invalid_company_selection(self):
        response = self.client.post(
            reverse_lazy('company-selector'),
            {
                'company': '-1',
            },
        )
        self.assertFalse(
            CompanyUserPermission.objects.filter(pk=-1).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)


class TestCompanyCreateView(TestCase):
    def setUp(self):
        self.company_constants = {
            'name': 'Eventbrite',
            'description': 'Bringing the world together through live experiences',
        }
        self.user = UserFactory()
        self.client = Client()
        self.client.force_login(self.user)

    def _make_post(self):
        return self.client.post(
            '/suppliersite/supplier/company/create',
            self.company_constants,
            follow=True,
        )

    def test_valid_company_creation(self):
        self._make_post()
        self.assertEqual(
            Company.objects.last().name,
            self.company_constants['name']
        )

    def test_valid_redirection_after_company_creation(self):
        response = self._make_post()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.redirect_chain[0][0], '/suppliersite/supplier')

    def test_company_user_assigment(self):
        self._make_post()
        self.assertEqual(
            CompanyUserPermission.objects.last().user, self.user
        )
        self.assertEqual(
            CompanyUserPermission.objects.last().company.name,
            self.company_constants['name']
        )
