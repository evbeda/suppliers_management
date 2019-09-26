from django.contrib import admin

from .models import (
    Company,
    Address,
    BankAccount,
    TaxPayerArgentina,
    CompanyUserPermission,
    Invoice,
    InvoiceArg
)

admin.site.register(Company)
admin.site.register(Address)
admin.site.register(BankAccount)
admin.site.register(TaxPayerArgentina)
admin.site.register(CompanyUserPermission)
admin.site.register(Invoice)
admin.site.register(InvoiceArg)
