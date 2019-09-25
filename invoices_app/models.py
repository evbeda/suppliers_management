from django.db import models
from users_app.models import User
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator


CURRENCIES = [
    ('ARS', 'ARS'),
    ('USD', 'USD')
    ]

INVOICE_SATUS = [
    ('1', 'NEW'),
    ('2', 'APPROVED'),
    ('3', 'CHANGES REQUEST'),
    ('4', 'REJECTED'),
    ('5', 'PAID'),
]

ARS_INVOICE_TYPES = [
    ('A', 'A'),
    ('C', 'C'),
]


class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return "Company:{}".format(self.name)


class CompanyUserPermission(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None
    )
    permission = None


class TaxPayer(models.Model):
    TaxPayerStates = [
        ("PEND", "Pending"),
        ("ACT", "Active"),
    ]
    workday_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    taxpayer_state = models.CharField(
        max_length=200,
        choices=TaxPayerStates,
        default="PEND",
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return "Name:{} Status:{}".format(self.name, self.taxpayer_state)


class TaxPayerArgentina(TaxPayer):
    razon_social = models.CharField(max_length=200)
    cuit = models.CharField(max_length=200)


class Address(models.Model):
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE)

    def __str__(self):
        return "ADDRESS \n Street: {} Number: {} Zip_Code: {} City: {} State: {} Country: {}".format(
                self.street, self.number, self.zip_code, self.city, self.state, self.country
            )


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=200, default='')
    account_type = models.CharField(max_length=200, default='')
    account_number = models.CharField(max_length=200, default='')
    identifier = models.CharField(max_length=200, default='')
    taxpayer = models.ForeignKey(
        TaxPayer,
        on_delete=models.CASCADE,
        default=None
    )

    def __str__(self):
        return "Bank:{} account_type:{} account_number:{} identifier:{}".format(
            self.bank_name,
            self.account_type,
            self.account_number,
            self.identifier)


class Invoice(models.Model):
    # eb_company = models.CharField(max_length=200)
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.PROTECT)
    currency = models.CharField(max_length=200, choices=CURRENCIES)
    status = models.CharField(max_length=40, choices=INVOICE_SATUS, default='NEW')
    po_number = models.CharField(max_length=200,help_text="ex: 12341234")
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
    net_amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    vat = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
