import factory

from supplier_app import PAYMENT_TERMS, PAYMENT_TYPES
from supplier_app.bank_info import BANK_INFO
from supplier_app.models import (Address, BankAccount, Company,
                                 CompanyUserPermission, TaxPayer,
                                 TaxPayerArgentina)
from users_app.factory_boy import UserFactory


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


class TaxPayerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TaxPayer

    workday_id = factory.Sequence(lambda n: "{}".format(n))
    business_name = factory.Sequence(lambda n: "Eventbrite {}".format(n))
    taxpayer_state = "PENDING"
    country = "AR"
    company = factory.SubFactory(CompanyFactory)


class TaxPayerArgentinaFactory(TaxPayerFactory):

    class Meta:
        model = TaxPayerArgentina

    cuit = "1234569"
    taxpayer_comments = "Justificacion falsa"
    payment_type = PAYMENT_TYPES[0][0]
    payment_term = PAYMENT_TERMS[0][0]


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    street = "Calle falsa"
    number = factory.Sequence(lambda n: "{}".format(n))
    zip_code = "5500"
    city = "Godoy Cruz"
    state = "Mendoza"
    country = "Argentina"
    taxpayer = factory.SubFactory(TaxPayerFactory)


class BankAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BankAccount

    bank_account_number = factory.Sequence(lambda n: "{}".format(n))
    taxpayer = factory.SubFactory(TaxPayerFactory)
    bank_info = BANK_INFO["BANCO DE LA NACION ARGENTINA"]
