# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-11 12:09
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


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
                ('bank_account_number', models.CharField(max_length=60, unique=True)),
                ('bank_info', models.IntegerField(choices=[(16, 'CITIBANK N.A.'), (7, 'BANCO DE GALICIA Y BUENOS AIRES S.A.'), (11, 'BANCO DE LA NACION ARGENTINA'), (17, 'BBVA BANCO FRANCES S.A.')], verbose_name='Bank name')),
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
            name='CompanyUniqueToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64)),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
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
            name='TaxPayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workday_id', models.CharField(max_length=200)),
                ('business_name', models.CharField(max_length=200)),
                ('taxpayer_state', models.CharField(choices=[('ACTIVE', 'Active'), ('CHANGE REQUIRED', 'Change required'), ('PENDING', 'Pending'), ('DENIED', 'Denied')], default='PENDING', max_length=200)),
                ('country', models.CharField(default='AR', max_length=50)),
                ('taxpayer_comments', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaxPayerArgentina',
            fields=[
                ('taxpayer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='supplier_app.TaxPayer')),
                ('cuit', models.CharField(max_length=20)),
                ('payment_type', models.CharField(choices=[('BANK', 'Bank')], default='BANK', max_length=20)),
                ('payment_term', models.IntegerField(choices=[(15, '15 days'), (30, '30 days')], default=15)),
                ('afip_registration_file', models.FileField(upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='AFIP registration certificate')),
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
