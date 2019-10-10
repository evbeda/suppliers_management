import uuid, hashlib

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from supplier_app import (
    TAXPAYER_STATUS,
    get_taxpayer_status_choices
)


class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name.capitalize()


class CompanyUserPermission(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=None
    )
    permission = None


class CompanyUniqueToken(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    datetime = models.DateTimeField(default=timezone.now)

    @property
    def assing_company_token(self):
        self.token = self._token_generator()

    def _token_generator(self):
        salt = uuid.uuid4().hex + str(self.company.id)
        return hashlib.sha256(salt.encode('utf-8')).hexdigest()


class TaxPayer(models.Model):

    workday_id = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200)
    taxpayer_state = models.CharField(
        max_length=200,
        choices=get_taxpayer_status_choices(),
        default="Pending",
    )
    country = models.CharField(max_length=50, default='AR')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return "Name:{} Status:{}".format(
            self.business_name,
            self.taxpayer_state
            )

    def get_taxpayer_child(self):
        return COUNTRIES[self.country].objects.get(pk=self.id)

    def approve_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['ACTIVE']

    def deny_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['DENIED']

    def has_workday_id(self):
        return True if self.workday_id else False


class TaxPayerArgentina(TaxPayer):
    cuit = models.CharField(max_length=200)
    comments = models.CharField(max_length=200)
    payment_type = models.CharField(max_length=200)
    AFIP_registration_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name='AFIP registration certificate',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        )
    witholding_taxes_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name='Certificate of no tax withholding of IVA, income or SUSS',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        )


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


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=200, default='')
    bank_code = models.CharField(max_length=200, default='')
    bank_account_number = models.CharField(max_length=200, default='')
    taxpayer = models.ForeignKey(
        TaxPayer,
        on_delete=models.CASCADE,
        default=None
    )
    bank_cbu_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name='CBU bank certificate',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

    def __str__(self):
        return "Bank:{} Account_number:{}".format(
            self.bank_name,
            self.bank_account_number,
        )
