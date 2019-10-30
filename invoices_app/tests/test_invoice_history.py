from django.urls import reverse

from invoices_app.tests.test_base import TestBase
from utils.history import invoice_history_comments


class TestInvoiceHistory(TestBase):

    def test_history_changes_diff(self):
        self.client.force_login(self.ap_user)
        old_po_number = self.invoice.po_number
        self.invoice.po_number = '4321'
        self.invoice.save()
        comments = invoice_history_comments(self.invoice)
        self.assertEqual(len(comments), 1)
        self.assertEqual(
            comments[0].message,
            'Changed: \nPO number from {} to {}\n'.format(
                old_po_number,
                self.invoice.po_number
            )
        )

    def test_history_invoices_view(self):
        self.client.force_login(self.ap_user)
        old_po_number = self.invoice.po_number
        self.invoice.po_number = '4321'
        new_po_number = self.invoice.po_number
        self.invoice.save()
        response = self.client.get(
            reverse('invoice-history', kwargs={'pk': self.invoice.id}),
        )
        self.assertContains(response, old_po_number)
        self.assertContains(response, new_po_number)
