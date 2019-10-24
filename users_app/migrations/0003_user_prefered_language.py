# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-24 15:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0002_group_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='prefered_language',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Espanol'), ('pt-br', 'Portuguese (Brazil)')], default='en', max_length=40),
        ),
    ]
