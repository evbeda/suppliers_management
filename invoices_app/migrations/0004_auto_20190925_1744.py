# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-25 17:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices_app', '0003_auto_20190925_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateField(),
        ),
    ]