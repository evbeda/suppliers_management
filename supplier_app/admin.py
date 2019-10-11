from django.contrib import admin

from supplier_app.models import (Address, BankAccount, Company,
                                 CompanyUserPermission, TaxPayerArgentina)

admin.site.register(Company)
admin.site.register(Address)
admin.site.register(BankAccount)
admin.site.register(TaxPayerArgentina)
admin.site.register(CompanyUserPermission)
