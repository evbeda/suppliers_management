# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-30 18:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_AP',
            field=models.BooleanField(default=False),
        ),
    ]
