# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-04 14:38
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=10)),
                ('zip_code', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(default='', max_length=200)),
                ('bank_code', models.CharField(default='', max_length=200)),
                ('bank_account_number', models.CharField(default='', max_length=200)),
                ('bank_cbu_file', models.FileField(upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='CBU bank certificate')),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CompanyUserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier_app.Company')),
            ],
        ),
        migrations.CreateModel(
            name='PDFFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_file_received', models.DateTimeField(auto_now=True)),
                ('pdf_file', models.FileField(blank=True, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
            ],
        ),
        migrations.CreateModel(
            name='TaxPayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workday_id', models.CharField(max_length=200)),
                ('business_name', models.CharField(max_length=200)),
                ('taxpayer_state', models.CharField(choices=[('ACTIVE', 'Active'), ('CHANGE REQUIRED', 'Change required'), ('PENDING', 'Pending'), ('REFUSED', 'Refused')], default='PENDING', max_length=200)),
                ('country', models.CharField(default='AR', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TaxPayerArgentina',
            fields=[
                ('taxpayer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplier_app.TaxPayer')),
                ('cuit', models.CharField(max_length=200)),
                ('comments', models.CharField(max_length=200)),
                ('payment_type', models.CharField(max_length=200)),
                ('AFIP_registration_file', models.FileField(upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='AFIP registration certificate')),
                ('witholding_taxes_file', models.FileField(upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='Certificate of no tax withholding of IVA, income or SUSS')),
            ],
            bases=('supplier_app.taxpayer',),
        ),
        migrations.AddField(
            model_name='taxpayer',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier_app.Company'),
        ),
    ]
