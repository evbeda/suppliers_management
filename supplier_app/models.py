from django.db import models
from django.conf import settings

from supplier_app import (
    TAXPAYER_STATUS
)
from django.core.validators import FileExtensionValidator


class PDFFile(models.Model):
    pdf_file_received = models.DateTimeField(auto_now=True)
    pdf_file = models.FileField(
       upload_to='file',
       blank=True,
       validators=[FileExtensionValidator(allowed_extensions=['pdf'])])


class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return "Company:{}".format(self.name)


class CompanyUserPermission(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=None
    )
    permission = None


class TaxPayer(models.Model):

    workday_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    taxpayer_state = models.CharField(
        max_length=200,
        choices=TAXPAYER_STATUS,
        default="PENDING",
    )
    country = models.CharField(max_length=50, default='AR')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return "Name:{} Status:{}".format(self.name, self.taxpayer_state)

    def get_taxpayer_child(self):
        return COUNTRIES[self.country].objects.get(pk=self.id)

    def get_taxpayer_childs():
        taxpayers = []
        for code, country_model in COUNTRIES.items():
            taxpayers.extend(country_model.objects.filter(country=code))
        return taxpayers


class TaxPayerArgentina(TaxPayer):
    razon_social = models.CharField(max_length=200)
    cuit = models.CharField(max_length=200)
    justificacion = models.CharField(max_length=200)
    forma_de_pago = models.CharField(max_length=200)


COUNTRIES = {
    'AR': TaxPayerArgentina,
}


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
    bank_code = models.CharField(max_length=200, default='')
    account_number = models.CharField(max_length=200, default='')
    taxpayer = models.ForeignKey(
        TaxPayer,
        on_delete=models.CASCADE,
        default=None
    )

    def __str__(self):
        return "Bank:{} bank_code:{} account_number:{}".format(
            self.bank_name,
            self.bank_code,
            self.account_number,
        )
