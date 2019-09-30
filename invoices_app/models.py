from django.db import models
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
from invoices_app import (
    CURRENCIES,
    INVOICE_STATUS,
    ARS_INVOICE_TYPES
)
from supplier_app.models import (
    TaxPayer
)


class Invoice(models.Model):
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.PROTECT)
    currency = models.CharField(max_length=200, choices=CURRENCIES)
    status = models.CharField(
        max_length=40,
        choices=INVOICE_STATUS,
        default='NEW'
    )
    po_number = models.CharField(max_length=200, help_text="ex: 12341234")
    invoice_date = models.DateField()
    invoice_date_received = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE
    )
    invoice_file = models.FileField(
        upload_to='file',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])])


class InvoiceArg(Invoice):
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
