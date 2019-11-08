# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-11-06 14:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices_app', '0002_auto_20191105_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalinvoice',
            name='status',
            field=models.CharField(choices=[('1', 'APPROVED'), ('2', 'PENDING'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID')], default='2', max_length=40, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('1', 'APPROVED'), ('2', 'PENDING'), ('3', 'CHANGES REQUESTED'), ('4', 'REJECTED'), ('5', 'PAID')], default='2', max_length=40, verbose_name='Status'),
        ),
    ]