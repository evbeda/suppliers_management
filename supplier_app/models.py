import hashlib
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from supplier_app import (
    PAYMENT_TERMS,
    PAYMENT_TYPES,
    TAXPAYER_STATUS,
    get_taxpayer_status_choices
)
from supplier_app.constants.bank_info import get_bank_info_choices
from supplier_app.constants.countries import get_countries_choices


class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
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
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def assing_company_token(self):
        self.token = self._token_generator()

    @property
    def is_token_expired(self):
        minutes = self._get_token_expiration_time()
        time_delta = (timezone.now() - self.created_at).total_seconds()/60
        return time_delta > minutes

    def _get_token_expiration_time(self):
        return 48 * 60

    def _token_generator(self):
        salt = uuid.uuid4().hex + str(self.company.id)
        return hashlib.sha256(salt.encode('utf-8')).hexdigest()


class EBEntity(models.Model):
    eb_name = models.CharField(
        max_length=15,
        verbose_name=_("Eventbrite entity name"),
        )
    eb_country = models.CharField(
        max_length=15,
        verbose_name=_("Country"),
        choices=get_countries_choices(),
        default=None,
    )

    def __str__(self):
        return self.eb_name


class TaxPayer(models.Model):

    workday_id = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200, verbose_name=_("Business name"))
    taxpayer_state = models.CharField(
        max_length=200,
        choices=get_taxpayer_status_choices(),
        default="PENDING",
    )
    country = models.CharField(
        max_length=50,
        choices=get_countries_choices(),
        verbose_name=_("Country")
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    taxpayer_date = models.DateField(auto_now_add=True, verbose_name=_("Creation date"))
    taxpayer_comments = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Comments"),
    )

    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return self.business_name

    @property
    def taxpayer_identifier(self):
        return self.get_taxpayer_child().get_taxpayer_identifier()

    @property
    def eb_entities(self):
        return [txe.eb_entity for txe in self.taxpayerebentity_set.all()]

    def get_taxpayer_child(self):
        return COUNTRIES[self.country].objects.get(pk=self.id)

    def approve_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Approved'].value

    def deny_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Denied'].value

    def change_required_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Change required'].value

    def change_to_pending_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Pending'].value

    def has_workday_id(self):
        return True if self.workday_id else False


class TaxPayerEBEntity(models.Model):
    eb_entity = models.ForeignKey(EBEntity)
    taxpayer = models.ForeignKey(TaxPayer)


class TaxPayerArgentina(TaxPayer):
    cuit = models.CharField(max_length=20)
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        default="BANK",
        verbose_name=_("Payment type")
    )
    payment_term = models.IntegerField(
        choices=PAYMENT_TERMS,
        default=15,
        verbose_name=_("Payment term")
    )
    afip_registration_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name=_('AFIP registration certificate'),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        )
    witholding_taxes_file = models.FileField(
        upload_to='file',
        blank=True,
        null=True,
        verbose_name=_('Certificate of no tax withholding of Tax liens, income or SUSS'),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        )

    def get_taxpayer_identifier(self):
        return self.cuit


COUNTRIES = {
    'AR': TaxPayerArgentina,
}


class Address(models.Model):
    street = models.CharField(max_length=100, verbose_name=_("Street"))
    number = models.CharField(max_length=10, verbose_name=_("Number"))
    zip_code = models.CharField(max_length=10, verbose_name=_("Zip code"))
    city = models.CharField(max_length=50, verbose_name=_("City"))
    state = models.CharField(max_length=50, verbose_name=_("State"))
    country = models.CharField(
        max_length=50,
        choices=get_countries_choices(),
        verbose_name=_("Country"),
    )
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE)

    history = HistoricalRecords()


class BankAccount(models.Model):
    bank_account_number = models.CharField(max_length=60, unique=True, verbose_name=_("Bank account number"))
    bank_info = models.IntegerField(
        choices=get_bank_info_choices(),
        verbose_name=_('Bank name')
    )
    taxpayer = models.ForeignKey(
        TaxPayer,
        on_delete=models.CASCADE,
        default=None
    )
    bank_cbu_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name=_('Bank account certificate'),
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )

    history = HistoricalRecords()

    def __str__(self):
        return "Account_number:{}".format(
            self.bank_account_number,
        )


class TaxpayerComment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=None
    )
    comment_date_received = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE)
