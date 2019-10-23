from decimal import Decimal

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models

from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from invoices_app import (
    ARS_INVOICE_TYPES,
    CURRENCIES,
    INVOICE_STATUS,
    INVOICE_STATUS_NEW,
)
from supplier_app.models import (
    TaxPayer
)

from utils.invoice_lookup import invoice_status_lookup


class Invoice(models.Model):

    class Meta:
        unique_together = ('taxpayer', 'invoice_number',)

    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.PROTECT)
    currency = models.CharField(max_length=200, choices=CURRENCIES, verbose_name=_('Currency'))
    status = models.CharField(
        max_length=40,
        choices=INVOICE_STATUS,
        default=invoice_status_lookup(INVOICE_STATUS_NEW),
        verbose_name=_('Status')
    )
    po_number = models.CharField(max_length=200, help_text="ex: 12341234", verbose_name=_('PO number'))
    invoice_date = models.DateField(verbose_name=_('Invoice date'))
    invoice_due_date = models.DateField(verbose_name=_('Due Date'))
    invoice_date_received = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Received'))
    invoice_number = models.CharField(max_length=20, verbose_name=_('Invoice Number'))
    invoice_type = models.CharField(max_length=200, choices=ARS_INVOICE_TYPES, verbose_name=_('Invoice Type'))
    net_amount = models.DecimalField(
        verbose_name=_('Net amount'),
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    vat = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name=_('Tax Liens'),
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_('Total'),
    )
    user = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE
    )
    invoice_file = models.FileField(
        upload_to='file',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name=_('Invoice File'),
    )

    po_file = models.FileField(
        upload_to='file',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name=_('PO file'),
    )

    history = HistoricalRecords()

    @property
    def taxpayer_name(self):
        return self.taxpayer.business_name


class Comment(models.Model):
    user = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.PROTECT
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT
    )

    message = models.CharField(max_length=200)
    comment_date_received = models.DateTimeField(auto_now_add=True)
    comment_file = models.FileField(
        upload_to='file',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    def __str__(self):
        return self.message
