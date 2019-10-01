import factory
from supplier_app.models import (
    Company,
    TaxPayer,
    TaxPayerArgentina,
)


class CompanyFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "CompanyTest{}".format(n))
    description = "Fake description"

    class Meta:
        model = Company


class TaxPayerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TaxPayer

    workday_id = factory.Sequence(lambda n: "{}".format(n))
    name = factory.Sequence(lambda n: "Eventbrite {}".format(n))
    taxpayer_state = "PENDING"
    country = "AR"


class TaxPayerArgentinaFactory(TaxPayerFactory):

    class Meta:
        model = TaxPayerArgentina

    razon_social = "Monotributista"
    cuit = "1234569"
    justificacion = "Justificacion falsa"
    forma_de_pago = "Banco"
