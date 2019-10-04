from django.urls import reverse

from invoices_app import (
    INVOICE_STATUS_APPROVED,
)

from invoices_app.tests.test_base import TestBase


class TestAP(TestBase):

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertContains(response, self.invoice_creation_valid_data.po_number)
        self.assertContains(response, self.invoice_creation_valid_data.taxpayer.business_name)

    def test_ap_invoices_list_are_in_new_status(self):
        self.client.force_login(self.ap_user)

        self.invoice_from_other_user.status = INVOICE_STATUS_APPROVED
        self.invoice_from_other_user.save()

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with NEW status should be listed.
        self.assertContains(
            response,
            self.invoice_creation_valid_data.taxpayer.business_name
        )
        self.assertNotContains(
            response,
            self.invoice_from_other_user.taxpayer.business_name
        )
