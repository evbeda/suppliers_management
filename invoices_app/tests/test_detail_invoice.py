from invoices_app.tests.test_base import TestBase

from http import HTTPStatus

from django.http import HttpResponseRedirect
from django.urls import reverse


class DetailInvoiceTest(TestBase):

    def test_click_in_row_invoice_redirects_to_detail_invoice(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice_creation_valid_data.taxpayer.id,
                        'pk': self.invoice_creation_valid_data.id,
                        }
                    ),
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_get_detail_invoice_without_login(self):
        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice_creation_valid_data.taxpayer.id,
                        'pk': self.invoice_creation_valid_data.id,
                        }
                    ),
        )
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(response.url, '/?next=/invoices/taxpayer/1/detail/1/')

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
        self.assertEqual(response.url, '/?next=/invoices/taxpayer/2/detail/2/')
