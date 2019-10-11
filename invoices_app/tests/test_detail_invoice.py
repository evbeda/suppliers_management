from http import HTTPStatus
from parameterized import parameterized

from django.http import HttpResponseRedirect
from django.urls import reverse

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
)
from invoices_app.factory_boy import InvoiceFactory
from invoices_app.models import Comment
from supplier_management_site.tests.test_base import TestBase

from supplier_app.tests.factory_boy import CompanyUserPermissionFactory

from users_app.factory_boy import UserFactory

from utils.invoice_lookup import invoice_status_lookup

class DetailInvoiceTest(TestBase):

    def test_click_in_row_invoice_redirects_to_detail_invoice(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice.taxpayer.id,
                        'pk': self.invoice.id,
                    }
            ),
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_get_detail_invoice_without_login(self):
        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice.taxpayer.id,
                        'pk': self.invoice.id,
                        }
                    ),
        )
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            response.url,
            '/?next=/invoices/taxpayer/{}/detail/{}/'.format(
                self.taxpayer.id,
                self.invoice.id,
            )
        )

    def test_get_detail_invoice_with_no_corresponding_supplier(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice_from_other_user.taxpayer.id,
                        'pk': self.invoice_from_other_user.id,
                        }
                    ),
        )

        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            response.url,
            '/?next=/invoices/taxpayer/{}/detail/{}/'.format(
                self.invoice_from_other_user.taxpayer.id,
                self.invoice_from_other_user.id,
            )
        )
