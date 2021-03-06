import factory
from unittest.mock import MagicMock
from django.utils import timezone
from django.core.files import File

from supplier_app.constants.payment_usa import TRANSACTION_TYPE_USA, ACCOUNT_TYPE_USA
from supplier_app.constants.usa_taxpayer_id_type import TAXPAYER_ID_TYPE
from supplier_app.models import (
    Address,
    BankAccount,
    Company,
    CompanyUniqueToken,
    CompanyUserPermission,
    EBEntity,
    TaxPayer,
    TaxPayerArgentina,
    TaxPayerEBEntity,
    TaxPayerUnitedStates,
    ContactInformation,
    EBEntityCompany,
    BankAccountUnitedStates,
)

from supplier_app.constants.bank_info import BANK_INFO
from supplier_app.constants.payment_ar import TRANSACTION_TYPE_AR, ACCOUNT_TYPE_AR
from supplier_app import (
    CURRENT_STATUS,
    PAYMENT_TERMS,
    PAYMENT_TYPES,
)
from users_app.factory_boy import (
    UserFactory,
)

file_mock = MagicMock(spec=File)
file_mock.name = 'test.pdf'
file_mock.size = 50


class EBEntityFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EBEntity

    eb_name = factory.Sequence(lambda n: "Eventbrite {}".format(n))
    eb_country = "AR"


class CompanyFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "CompanyTest{}".format(n))
    description = "Fake description"

    class Meta:
        model = Company


class CompanyUserPermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompanyUserPermission

    company = factory.SubFactory(CompanyFactory)
    user = factory.SubFactory(UserFactory)


class EbEntityCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EBEntityCompany

    company = factory.SubFactory(CompanyFactory)
    eb_entity = factory.SubFactory(EBEntityFactory)


class CompanyUniqueTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompanyUniqueToken

    company = factory.SubFactory(CompanyFactory)
    token = 'f360da6197be4436a4b686460289085c14a859d634a9daca2d7d137b178b193e'
    created_at = timezone.now()


class TaxPayerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TaxPayer

    workday_id = factory.Sequence(lambda n: "{}".format(n))
    business_name = factory.Sequence(lambda n: "Eventbrite {}".format(n))
    taxpayer_state = "PENDING"
    company = factory.SubFactory(CompanyFactory)
    country = "AR"
    new_comment_from_supplier = True
    new_comment_from_ap = True


class TaxPayerEBEntityFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TaxPayerEBEntity

    eb_entity = factory.SubFactory(EBEntityFactory)
    taxpayer = factory.SubFactory(TaxPayerFactory)
    status = CURRENT_STATUS


class TaxPayerArgentinaFactory(TaxPayerFactory):

    class Meta:
        model = TaxPayerArgentina

    afip_registration_file = file_mock
    cuit = factory.Sequence(lambda n: "{}".format(n))
    payment_type = PAYMENT_TYPES[0][0]
    payment_term = PAYMENT_TERMS[0][0]
    witholding_taxes_file = file_mock
    afip_no_retention_taxes_file = file_mock
    iibb_registration_file = file_mock
    iibb_no_retention_taxes_file = file_mock
    taxpayer_condition = "monotributista"


class TaxPayerUnitedStatedFactory(TaxPayerFactory):

    class Meta:
        model = TaxPayerUnitedStates

    taxpayer_id_number = factory.Sequence(lambda n: "{}".format(n))
    taxpayer_id_number_type = TAXPAYER_ID_TYPE["EIN"]
    payment_type = PAYMENT_TYPES[0][0]
    payment_term = PAYMENT_TERMS[0][0]
    w9_file = file_mock


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    street = "Calle falsa"
    number = factory.Sequence(lambda n: "{}".format(n))
    zip_code = "5500"
    city = "Godoy Cruz"
    state = "Mendoza"
    country = "AR"
    taxpayer = factory.SubFactory(TaxPayerFactory)


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContactInformation

    contact_person = "John Smith"
    phone_number = "0115123456"
    email = "jhonsmith@gmail.com"
    website = "www.website.com"
    address = factory.SubFactory(AddressFactory)
    taxpayer = factory.SubFactory(TaxPayerFactory)


class BankAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankAccount

    bank_account_number = factory.Sequence(lambda n: "{}".format(n))
    taxpayer = factory.SubFactory(TaxPayerFactory)
    bank_transaction_type = TRANSACTION_TYPE_AR['Bank transfer']
    bank_account_type = ACCOUNT_TYPE_AR['Saving account']
    bank_beneficiary = 'John Smith'
    bank_info = BANK_INFO["BANCO DE LA NACION ARGENTINA"]
    bank_cbu_file = file_mock


class BankAccountUnitedStatesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankAccountUnitedStates

    bank_account_number = factory.Sequence(lambda n: "{}".format(n))
    bank_name = 'First Bank'
    bank_address = '15th Street, Transylvania'
    taxpayer = factory.SubFactory(TaxPayerFactory)
    bank_transaction_type = TRANSACTION_TYPE_USA['Wire']
    bank_account_type = ACCOUNT_TYPE_USA['Saving account']
    bank_beneficiary = 'John Smith'
    routing_number = factory.Sequence(lambda n: "{}".format(n))
    remit_address = factory.SubFactory(AddressFactory)
