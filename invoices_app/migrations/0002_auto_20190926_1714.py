# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-26 17:14
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_file',
            field=models.FileField(blank=True, default=None, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='po_number',
            field=models.CharField(help_text='ex: 12341234', max_length=200),
        ),
    ]
