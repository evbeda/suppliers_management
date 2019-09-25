# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-25 11:59
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PDFFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf_file', models.FileField(blank=True, upload_to='file', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
            ],
        ),
    ]
