# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-04-30 12:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_app', '0019_contactinformation_historicalcontactinformation'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='eb_entity',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='supplier_app.EBEntity'),
        ),
    ]