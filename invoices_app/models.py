from decimal import Decimal

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
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
    currency = models.CharField(max_length=200, choices=CURRENCIES)
    status = models.CharField(
        max_length=40,
        choices=INVOICE_STATUS,
        default=invoice_status_lookup(INVOICE_STATUS_NEW)
    )
    po_number = models.CharField(max_length=200, help_text="ex: 12341234")
    invoice_date = models.DateField()
    invoice_due_date = models.DateField()
    invoice_date_received = models.DateTimeField(auto_now_add=True)
    invoice_number = models.CharField(max_length=20)
    invoice_type = models.CharField(max_length=200, choices=ARS_INVOICE_TYPES)
    net_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    vat = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    user = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE
    )
    invoice_file = models.FileField(
        upload_to='file',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    po_file = models.FileField(
        upload_to='file',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

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
