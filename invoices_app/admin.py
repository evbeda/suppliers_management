from django.contrib import admin

from .models import (
    Company,
    Address,
    BankAccount,
    TaxPayerArgentina
)

admin.site.register(Company)
admin.site.register(Address)
admin.site.register(BankAccount)
admin.site.register(TaxPayerArgentina)
