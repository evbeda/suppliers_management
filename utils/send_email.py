from django.conf import settings
from django.core.mail import send_mail
from supplier_app.models import Company, CompanyUserPermission


def send_email_notification(subject, message, recipient_list):
    email_from = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message,
        'Suppliers Management Eventbrite <jx3.team@gmail.com>',
        recipient_list,
        fail_silently=False,
    )


def get_user_emails_by_tax_payer_id(tax_payer_id):
    company = Company.objects.get(pk=tax_payer_id)
    emails = CompanyUserPermission.objects.values_list('user__email', flat=True).filter(company=company)
    return list(emails)

