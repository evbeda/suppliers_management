# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-10 03:46
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supplier_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=200)),
                ('comment_date_received', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalInvoice',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('currency', models.CharField(choices=[('ARS', 'ARS'), ('USD', 'USD')], max_length=200)),
                ('status', models.CharField(choices=[('1', 'APPROVED'), ('2', 'NEW'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID')], default='2', max_length=40)),
                ('po_number', models.CharField(help_text='ex: 12341234', max_length=200)),
                ('invoice_date', models.DateField()),
                ('invoice_date_received', models.DateTimeField(blank=True, editable=False)),
                ('invoice_number', models.CharField(max_length=20)),
                ('invoice_type', models.CharField(choices=[('A', 'A'), ('C', 'C')], max_length=200)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('vat', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('invoice_file', models.TextField(blank=True, max_length=100, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('po_file', models.TextField(blank=True, max_length=100, null=True, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('taxpayer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='supplier_app.TaxPayer')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical invoice',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('ARS', 'ARS'), ('USD', 'USD')], max_length=200)),
                ('status', models.CharField(choices=[('1', 'APPROVED'), ('2', 'NEW'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID')], default='2', max_length=40)),
                ('po_number', models.CharField(help_text='ex: 12341234', max_length=200)),
                ('invoice_date', models.DateField()),
                ('invoice_date_received', models.DateTimeField(auto_now_add=True)),
                ('invoice_number', models.CharField(max_length=20)),
                ('invoice_type', models.CharField(choices=[('A', 'A'), ('C', 'C')], max_length=200)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('vat', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('invoice_file', models.FileField(blank=True, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('po_file', models.FileField(blank=True, null=True, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('taxpayer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='supplier_app.TaxPayer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='invoices_app.Invoice'),
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='invoice',
            unique_together=set([('taxpayer', 'invoice_number')]),
        ),
    ]
