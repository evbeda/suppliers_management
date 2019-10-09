from django.urls import reverse

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_REJECTED
)

from invoices_app.tests.test_base import TestBase

from utils.invoice_lookup import invoice_status_lookup

class TestAP(TestBase):

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertContains(response, self.invoice.po_number)
        self.assertContains(response, self.invoice.taxpayer.business_name)

    def test_ap_invoices_list_are_in_new_status(self):
        self.client.force_login(self.ap_user)

        self.invoice_from_other_user.status = invoice_status_lookup(INVOICE_STATUS_REJECTED)
        self.invoice_from_other_user.save()

        response = self.client.get(
            '{}?{}'.format(
                reverse('invoices-list'),
                'status={}'.format(
                    invoice_status_lookup(INVOICE_STATUS_NEW)
                )
            )
        )
        # Only the invoice with NEW status should be listed
        self.assertNotContains(
            response,
            self.invoice_from_other_user.invoice_number
        )
        self.assertContains(
            response,
            self.invoice.invoice_number
        )
