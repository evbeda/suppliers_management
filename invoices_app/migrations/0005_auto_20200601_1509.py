# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-06-01 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices_app', '0004_auto_20191113_2006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalinvoice',
            name='invoice_type',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='invoice_type',
        ),
        migrations.AlterField(
            model_name='historicalinvoice',
            name='status',
            field=models.CharField(choices=[('1', 'APPROVED'), ('2', 'PENDING'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID'), ('6', 'IN PROGRESS')], default='2', max_length=40, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('1', 'APPROVED'), ('2', 'PENDING'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID'), ('6', 'IN PROGRESS')], default='2', max_length=40, verbose_name='Status'),
        ),
    ]
