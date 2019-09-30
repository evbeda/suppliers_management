from django.contrib import admin

from .models import (
    Invoice,
    InvoiceArg,
)

admin.site.register(Invoice)
admin.site.register(InvoiceArg)
