from django.core.mail import send_mail
from supplier_app.models import Company, CompanyUserPermission
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email_notification(subject, message, recipient_list):
    plain_message = strip_tags(message)
    send_mail(
        subject,
        plain_message,
        'Suppliers Management Eventbrite <jx3.team@gmail.com>',
        recipient_list,
        html_message=message,
        fail_silently=False,
    )


def get_user_emails_by_tax_payer_id(tax_payer_id):
    company = Company.objects.get(pk=tax_payer_id)
    emails = CompanyUserPermission.objects.values_list('user__email', flat=True).filter(company=company)
    return list(emails)


def build_mail_html(supplier_name, upper_text, lower_text):
    html_message = render_to_string(
        'mail_template.html',
        {
            'supplier_name': supplier_name,
            'upper_text': upper_text,
            'lower_text': lower_text,
        }
    )

    return html_message
