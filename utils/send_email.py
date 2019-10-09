from django.conf import settings
from django.core.mail import send_mail
from supplier_app.models import Company, CompanyUserPermission


def send_email_notification(subject, message, recipient_list):
    email_from = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message,
        email_from,
        recipient_list,
        fail_silently=False,
    )


def get_user_emails_from_tax_payer(tax_payer):
    company = Company.objects.get(pk=tax_payer.id)
    emails = CompanyUserPermission.objects.values_list('user__email', flat=True).filter(company=company)
    return list(emails)
