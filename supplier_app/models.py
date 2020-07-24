import hashlib
import uuid

from django.conf import settings
from django.core.validators import (
    FileExtensionValidator,
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords


from supplier_app import (
    BANK_ACCOUNT_MAX_SIZE_FILE,
    BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS,
    PAYMENT_TERMS,
    PAYMENT_TYPES,
    TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
    TAXPAYER_ALLOWED_FILE_EXTENSIONS,
)
from supplier_app.constants.payment_usa import (
    get_transaction_type_usa_info_choices,
    get_account_type_info_usa_choices,
)

from supplier_app.constants.taxpayer_status import (
    TAXPAYER_STATUS,
    get_taxpayer_status_choices,
)
from supplier_app.constants.bank_info import get_bank_info_choices
from supplier_app.constants.countries import get_countries_choices
from supplier_app.constants.conditions import get_conditions_choices
from supplier_app.constants.eb_entities_status import (
    CURRENT_STATUS,
    UNUSED_STATUS,
)
from supplier_app.constants.taxpayer_status import (
    TAXPAYER_STATUS,
    get_taxpayer_status_choices,
)
from supplier_app.constants.payment_ar import (
    get_transaction_type_info_choices,
    get_account_type_info_choices,
)
from supplier_app.constants.usa_taxpayer_id_type import get_usa_taxpayer_id_info_choices
from utils.file_validator import FileSizeValidator


class EBEntity(models.Model):
    eb_name = models.CharField(
        max_length=50,
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


class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField()

    def __str__(self):
        return self.name.capitalize()


class EBEntityCompany(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    eb_entity = models.ForeignKey(EBEntity, on_delete=models.CASCADE, default=None)


class InvitingBuyer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    inviting_buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=None
    )
    creation_date = models.DateTimeField(auto_now_add=True)


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


class TaxPayer(models.Model):

    workday_id = models.CharField(max_length=50)
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
    new_comment_from_supplier = models.BooleanField(default=False)
    new_comment_from_ap = models.BooleanField(default=False)
    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return self.business_name

    @property
    def taxpayer_identifier(self):
        return self.get_taxpayer_child().get_taxpayer_identifier()

    @property
    def eb_entities(self):
        return [txe.eb_entity for txe in self.taxpayerebentity_set.filter(status=CURRENT_STATUS)]

    @property
    def get_eb_entity(self):
        for txe in self.taxpayerebentity_set.filter(status=CURRENT_STATUS):
            return txe.eb_entity.eb_name

    @property
    def get_badge(self):
        return TAXPAYER_STATUS[self.taxpayer_state.title()]['css-class']

    def get_taxpayer_child(self):
        return COUNTRIES[self.country].objects.get(pk=self.id)

    def approve_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Approved']['choices'].value

    def deny_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Denied']['choices'].value

    def in_progress_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['In Progress']['choices'].value

    def change_required_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Change Required']['choices'].value

    def set_changes_pending_taxpayer(self):
        self.taxpayer_state = TAXPAYER_STATUS['Changes Pending']['choices'].value

    def has_workday_id(self):
        return True if self.workday_id else False

    def set_current_eb_entities(self, eb_entities):
        eb_entities_id = [eb_entity.id for eb_entity in eb_entities]

        self.create_if_not_exist_taxpayer_eb_entity(eb_entities)

        taxpayer_eb_entity_selected = self.taxpayerebentity_set.filter(
            eb_entity__pk__in=eb_entities_id
        )
        taxpayer_eb_entity_non_selected = self.taxpayerebentity_set.exclude(
            eb_entity__pk__in=eb_entities_id
        )
        self.apply_function_to_all_elems(
            taxpayer_eb_entity_selected,
            TaxPayerEBEntity.set_current_status
        )
        self.apply_function_to_all_elems(
            taxpayer_eb_entity_non_selected,
            TaxPayerEBEntity.set_unused_status
        )

    def apply_function_to_all_elems(self, default_list, function):
        for elem in default_list:
            function(elem)

    def create_if_not_exist_taxpayer_eb_entity(self, eb_entities):
        for eb_entity in eb_entities:
            if not self.taxpayerebentity_set.filter(eb_entity__pk=eb_entity.id):
                TaxPayerEBEntity.objects.create(
                    taxpayer=self,
                    eb_entity=eb_entity,
                )


class TaxPayerEBEntity(models.Model):
    eb_entity = models.ForeignKey(EBEntity)
    taxpayer = models.ForeignKey(TaxPayer)
    status = models.CharField(
        max_length=10,
        choices=(
            (1, "Current"),
            (2, "Unused")
        ),
        default=1,
    )

    def set_current_status(taxpayer_eb_entity):
        taxpayer_eb_entity.status = CURRENT_STATUS
        taxpayer_eb_entity.save()

    def set_unused_status(taxpayer_eb_entity):
        taxpayer_eb_entity.status = UNUSED_STATUS
        taxpayer_eb_entity.save()


class TaxPayerArgentina(TaxPayer):
    cuit = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                r'^[0-9]+$',
                message=_('CUIT must only have numbers'),
                code='invalid_cuit'
            ),
            MaxLengthValidator(12),
            MinLengthValidator(11),
        ]
    )
    taxpayer_condition = models.CharField(
        max_length=100,
        choices=get_conditions_choices(),
        verbose_name=_("Taxpayer Condition"),
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        default="BANK",
        verbose_name=_("Payment type")
    )
    payment_term = models.IntegerField(
        choices=PAYMENT_TERMS,
        verbose_name=_("Payment term")
    )
    afip_registration_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name=_('AFIP registration certificate'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
                ),
            ],
        )
    # Constancia de no Retencion
    afip_no_retention_taxes_file = models.FileField(
        upload_to='file',
        blank=True,
        null=True,
        verbose_name=_('AFIP No Retention'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
            ),
        ],
    )
    # IIBB Constancia de Inscripcion
    iibb_registration_file = models.FileField(
        upload_to='file',
        blank=True,
        null=True,
        verbose_name=_('IIBB registration certificate'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
            ),
        ],
    )
    # Constancia de no Retencion IIBB
    iibb_no_retention_taxes_file = models.FileField(
        upload_to='file',
        blank=True,
        null=True,
        verbose_name=_('IIBB No Retention'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
            ),
        ],
    )
    witholding_taxes_file = models.FileField(
        upload_to='file',
        blank=True,
        null=True,
        verbose_name=_('Certificate of no income withholding'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
            ),
        ],
    )
    witholding_suss_file = models.FileField(
        upload_to='file',
        blank=True,
        null=True,
        verbose_name=_('Certificate of no SUSS withholding'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
            ),
        ],
    )

    def get_taxpayer_identifier(self):
        return self.cuit


class TaxPayerUnitedStates(TaxPayer):
    taxpayer_id_number = models.CharField(
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(
                r'^[0-9]+$',
                message=_('Id number must only have numbers'),
                code='invalid_id'
            ),
            MaxLengthValidator(9),
            MinLengthValidator(9),
        ]
    )
    taxpayer_id_number_type = models.IntegerField(
        choices=get_usa_taxpayer_id_info_choices(),
        verbose_name=_('Taxpayer id type')
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPES,
        default="BANK",
        verbose_name=_("Payment type")
    )
    payment_term = models.IntegerField(
        choices=PAYMENT_TERMS,
        verbose_name=_("Payment term")
    )
    w9_file = models.FileField(
        upload_to='file',
        blank=False,
        verbose_name=_('W9 certificate'),
        validators=[
            FileExtensionValidator(allowed_extensions=TAXPAYER_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=TAXPAYER_CERTIFICATE_MAX_SIZE_FILE,
                code='invalid_file_size',
                ),
            ],
        )

    def get_taxpayer_identifier(self):
        return self.taxpayer_id_number


COUNTRIES = {
    'AR': TaxPayerArgentina,
    'USA': TaxPayerUnitedStates,
}


class Address(models.Model):
    street = models.CharField(
        max_length=100,
        verbose_name=_("Street"),
    )
    number = models.IntegerField(verbose_name=_("Number"))
    zip_code = models.CharField(max_length=10, verbose_name=_("Zip code"))
    city = models.CharField(
        max_length=50,
        verbose_name=_("City"),
    )
    state = models.CharField(
        max_length=50,
        verbose_name=_("State"),
        validators=[
            RegexValidator(
                r'\D',
                message=_('City name must only have letters'),
                code='invalid_city'
            ),
        ],
    )
    country = models.CharField(
        max_length=50,
        choices=get_countries_choices(),
        verbose_name=_("Country"),
    )
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE)
    history = HistoricalRecords()


class ContactInformation(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    history = HistoricalRecords()
    contact_person = models.CharField(max_length=100, verbose_name=_("Contact person"))
    phone_number = models.CharField(max_length=20,verbose_name=_("Phone number"))
    email = models.CharField(max_length=100, verbose_name=_("Email"))
    website = models.CharField(max_length=100, verbose_name=_("Web site"), blank=True)
    taxpayer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE, default=None)


class BankAccount(models.Model):
    bank_account_number = models.CharField(
        max_length=22,
        unique=True,
        verbose_name=_("Bank account number"),
        validators=[
            RegexValidator(
                r'^[0-9]+$',
                message=_('Bank account must only have numbers'),
                code='invalid_bank_number',),
            MinLengthValidator(22),
            MaxLengthValidator(22),
        ]
    )
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
        validators=[
            FileExtensionValidator(allowed_extensions=BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS),
            FileSizeValidator(
                limit_size=BANK_ACCOUNT_MAX_SIZE_FILE,
                code='invalid_file_size',
            ),
        ],
    )
    bank_transaction_type = models.IntegerField(
        choices=get_transaction_type_info_choices(),
        verbose_name=_('Payment method')
    )
    bank_account_type = models.IntegerField(
        choices=get_account_type_info_choices(),
        verbose_name=_('Account type')
    )
    bank_beneficiary = models.CharField(
        max_length=60,
        verbose_name=_("Beneficiary"),
        default=None
    )

    history = HistoricalRecords()

    def __str__(self):
        return "Account_number:{}".format(
            self.bank_account_number,
        )


class BankAccountUnitedStates(models.Model):
    bank_account_number = models.CharField(
        max_length=22,
        unique=True,
        verbose_name=_("Bank account number"),
        validators=[
            RegexValidator(
                r'^[0-9]+$',
                message=_('Bank account must only have numbers'),
                code='invalid_bank_number',),
        ]
    )
    bank_name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Bank name"),
    )
    bank_address = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Bank address"),
    )
    taxpayer = models.ForeignKey(
        TaxPayer,
        on_delete=models.CASCADE,
        default=None
    )
    bank_transaction_type = models.IntegerField(
        choices=get_transaction_type_usa_info_choices(),
        verbose_name=_('Payment method')
    )
    bank_account_type = models.IntegerField(
        choices=get_account_type_info_usa_choices(),
        verbose_name=_('Account type')
    )
    bank_beneficiary = models.CharField(
        max_length=60,
        verbose_name=_("Beneficiary"),
        default=None
    )
    routing_number = models.CharField(
        max_length=22,
        unique=True,
        verbose_name=_("Routing number"),
        validators=[
            RegexValidator(
                r'^[0-9]+$',
                message=_('Routing number must only have numbers'),
                code='invalid_routing_number', ),
        ]
    )
    remit_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        default=None
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

    class Meta:
        ordering = ['-comment_date_received']
