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
            ('can_view_invoices', 'Can view invoices', content_type),
            ('can_view_supplier_invoices', 'Can view supplier invoices', content_type),
            ('can_view_taxpayer', 'Can view taxpayers', content_type),
            ('can_create_taxpayer', 'Can create taxpayer', content_type),
            ('can_create_invoice', 'Can create invoice', content_type),
            ('can_edit_taxpayer', 'Can edit taxpayer', content_type),
            ('can_edit_taxpayer_address', 'Can edit taxpayer address', content_type),
            ('can_edit_taxpayer_bank_account', 'Can edit taxpayer bank account', content_type),
            ('can_edit_invoice', 'Can edit invoice', content_type),
            ('supplier_role', 'Is supplier', content_type),
        ],
        'ap_admin': [
            ('can_view_invoices', 'Can view invoices', content_type),
            ('can_view_all_invoices', 'Can view all invoices', content_type),
            ('can_view_invoices_history', 'Can view invoice history', content_type),
            ('can_view_taxpayer_history', 'Can view taxpayer history', content_type),
            ('can_view_taxpayer', 'Can view taxpayers', content_type),
            ('can_view_all_taxpayers', 'Can view all taxpayers', content_type),
            ('can_edit_taxpayer', 'Can edit taxpayer', content_type),
            ('can_edit_taxpayer_address', 'Can edit taxpayer address', content_type),
            ('can_edit_taxpayer_bank_account', 'Can edit taxpayer bank account', content_type),
            ('can_edit_invoice', 'Can edit invoice', content_type),
            ('can_change_invoice_status', 'Can edit invoice', content_type),
            ('can_approve', 'Can approve', content_type),
            ('can_reject', 'Can reject', content_type),
            ('can_request_change', 'Can request changes', content_type),
            ('ap_role', 'Is ap', content_type),
            ('can_create_company', 'Can create company', content_type),
            ('can_send_company_invite', 'Can send company invite', content_type),
        ],
        'ap_reporter': [
            ('can_view_invoices', 'Can view invoices', content_type),
            ('can_view_all_invoices', 'Can view all invoices', content_type),
            ('can_view_all_taxpayers', 'Can view all taxpayers', content_type),
            ('can_view_reports', 'Can view reports', content_type),
            ('ap_role', 'Is ap', content_type),
        ],
        'ap_manager': [
            ('can_view_invoices', 'Can view invoices', content_type),
            ('can_view_all_invoices', 'Can view all invoices', content_type),            
            ('can_view_all_taxpayers', 'Can view all taxpayers', content_type),
            ('can_manage_aps', 'Can manage ap permissions', content_type),
            ('ap_role', 'Is ap', content_type),
        ],
        'ap_buyer': [
            ('can_create_company', 'Can create company', content_type),
            ('can_send_company_invite', 'Can send company invite', content_type),
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
