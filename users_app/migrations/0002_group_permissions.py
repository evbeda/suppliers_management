# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-14 16:51
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.models import ContentType
from utils.permissions import create_groups_and_apply_permisssions


def add_group_permissions(*args, **kwargs):
    content_type, _ = ContentType.objects.get_or_create(app_label='users_app', model='user')

    groups = {
        'supplier': [
            ('can_view_supplier', 'Can access supplier views', content_type),
            ('can_create_taxpayer', 'Can create taxpayer', content_type),
            ('can_create_invoice', 'Can create invoice', content_type),
        ],
        'ap_admin': [
            ('can_view_ap', 'Can view', content_type),
            ('can_edit_taxpayer', 'Can edit taxpayer', content_type),
            ('can_edit_invoice', 'Can edit invoice', content_type),
            ('can_approve', 'Can approve', content_type),
            ('can_reject', 'Can reject', content_type),
            ('can_request_change', 'Can request changes', content_type),
            ('can_pay_invoice', 'Can pay invoices', content_type),
        ],
        'ap_reporter': [
            ('can_view_ap', 'Can view', content_type),
            ('can_view_reports', 'Can view reports', content_type),
        ],
        'ap_manager': [
            ('can_manage_aps', 'Can manage ap permissions', content_type),
        ],
    }

    create_groups_and_apply_permisssions(groups)


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_group_permissions),
    ]
