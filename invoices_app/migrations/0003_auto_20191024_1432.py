# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-24 14:32
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices_app', '0002_auto_20191018_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalinvoice',
            name='currency',
            field=models.CharField(choices=[('ARS', 'ARS'), ('USD', 'USD')], max_length=200, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='invoice_date',
            field=models.DateField(verbose_name='Invoice date'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='invoice_date_received',
            field=models.DateTimeField(blank=True, editable=False, verbose_name='Date Received'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='invoice_due_date',
            field=models.DateField(verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='invoice_file',
            field=models.TextField(blank=True, max_length=100, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='Invoice File'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='invoice_number',
            field=models.CharField(max_length=20, verbose_name='Invoice Number'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='invoice_type',
            field=models.CharField(choices=[('A', 'A'), ('C', 'C')], max_length=200, verbose_name='Invoice Type'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='net_amount',
            field=models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Net amount'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='po_file',
            field=models.TextField(blank=True, max_length=100, null=True, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='PO file'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='po_number',
            field=models.CharField(help_text='ex: 12341234', max_length=200, verbose_name='PO number'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='status',
            field=models.CharField(choices=[('1', 'APPROVED'), ('2', 'NEW'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID')], default='2', max_length=40, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='vat',
            field=models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Tax Liens'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='currency',
            field=models.CharField(choices=[('ARS', 'ARS'), ('USD', 'USD')], max_length=200, verbose_name='Currency'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date',
            field=models.DateField(verbose_name='Invoice date'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_date_received',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date Received'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_due_date',
            field=models.DateField(verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_file',
            field=models.FileField(blank=True, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='Invoice File'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(max_length=20, verbose_name='Invoice Number'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_type',
            field=models.CharField(choices=[('A', 'A'), ('C', 'C')], max_length=200, verbose_name='Invoice Type'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='net_amount',
            field=models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Net amount'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='po_file',
            field=models.FileField(blank=True, null=True, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='PO file'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='po_number',
            field=models.CharField(help_text='ex: 12341234', max_length=200, verbose_name='PO number'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('1', 'APPROVED'), ('2', 'NEW'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID')], default='2', max_length=40, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='vat',
            field=models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Tax Liens'),
        ),
    ]
