# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-11-01 14:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplier_app', '0002_auto_20191031_1946'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taxpayercomment',
            options={'ordering': ['-comment_date_received']},
        ),
    ]
