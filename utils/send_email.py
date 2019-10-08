from django.conf import settings
from django.core.mail import send_mail


def send_email_notification(subject, message, recipient_list):
    email_from = settings.EMAIL_HOST_USER
    send_mail(
        subject,
        message,
        email_from,
        recipient_list,
        fail_silently=False,
    )
