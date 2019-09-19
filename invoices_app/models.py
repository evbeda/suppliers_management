from django.db import models
from users_app.models import User
from django.conf import settings
from datetime import datetime


class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return "Company:{} Description:{}".format(self.name, self.description)


class TaxPayerState(models.Model):
    name_tax_payer_state = models.CharField(default="Pending", max_length=200)

    def __str__(self):
        return "Status: {}".format(self.name_tax_payer_state)


class CompanyUserPermission(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None
    )
    permission = None


class TaxPayer(models.Model):
    workday_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    tax_payer_state = models.ForeignKey(TaxPayerState, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class TaxPayerArgentina(TaxPayer):
    razon_social = models.CharField(max_length=200)
    cuit = models.CharField(max_length=200)

    def __str__(self):
        return "Razon Social: {} CUIT: {}".format(self.razon_social, self.cuit)


class Address(models.Model):
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    tax_payer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE)

    def __str__(self):
        return "ADDRESS \n Street: {} Number: {} Zip_Code: {} City: {} State: {} Country: {}".format(
                self.street, self.number, self.zip_code, self.city, self.state, self.country
            )


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=200)
    account_number = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200)
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
    #eb_company = models.CharField(max_length=200)
    tax_payer = models.ForeignKey(TaxPayer, on_delete=models.)
    currency = models.CharField(max_length=200)
    po_number = models.CharField(max_length=200)
    invoice_date = models.DateTimeField(auto_now=True)
    invoice_date_received = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.CASCADE
    )
    pdf_url = models.CharField(max_length=200)
