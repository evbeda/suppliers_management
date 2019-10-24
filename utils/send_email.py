from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import (
    ugettext_lazy as _,
    activate,
)

from supplier_app.models import (
    Company,
    CompanyUserPermission,
    TaxPayer,
)
from supplier_app import email_notifications

from utils.exceptions import CouldNotSendEmailError


def send_email_notification(subject, message, recipient_list):
    plain_message = strip_tags(message)
    try:
        send_mail(
            subject,
            plain_message,
            'Suppliers Management Eventbrite <{}>'.format(
                settings.EMAIL_HOST_USER
            ),
            recipient_list,
            html_message=message,
            fail_silently=False,
        )
    except Exception:
        raise CouldNotSendEmailError()


def company_invitation_notification(company, token, email, language):
    activate(language)
    subject = _(email_notifications['company_invitation']['subject'])
    upper_text = _(email_notifications['company_invitation']['body']['upper_text'])
    lower_text = _(email_notifications['company_invitation']['body']['lower_text'])
    btn_text = _(email_notifications['company_invitation']['body']['btn_text'])
    btn_url = email_notifications['company_invitation']['body']['btn_url']
    send_email_notification(
        subject,
        build_mail_html(
            company.name,
            upper_text,
            lower_text,
            btn_text,
            '{}/{}'.format(btn_url, token),
        ),
        email,
    )


def taxpayer_notification(taxpayer, change_type):
    subject = _(email_notifications[change_type]['subject'])
    upper_text = _(email_notifications[change_type]['body']['upper_text'])
    lower_text = _(email_notifications[change_type]['body']['lower_text'])
    btn_text = _(email_notifications[change_type]['body']['btn_text'])
    btn_url = email_notifications[change_type]['body']['btn_url']
    send_email_notification(
        subject,
        build_mail_html(
            taxpayer.business_name,
            upper_text,
            lower_text,
            btn_text,
            btn_url,
        ),
        get_user_emails_by_tax_payer_id(taxpayer.id)
    )


def get_user_emails_by_tax_payer_id(tax_payer_id):
    taxpayer = TaxPayer.objects.get(pk=tax_payer_id)
    company = Company.objects.get(pk=taxpayer.company.id)
    emails = CompanyUserPermission.objects.values_list(
        'user__email',
        flat=True,
    ).filter(company=company)
    return list(emails)


def build_mail_html(
    supplier_name,
    upper_text,
    lower_text,
    btn_text='Go to BriteSu',
    btn_url=settings.SUPPLIER_HOME_URL,
):
    html_message = render_to_string(
        'mail_template.html',
        {
            'supplier_name': supplier_name,
            'upper_text': upper_text,
            'lower_text': lower_text,
            'btn_text': btn_text,
            'btn_url': btn_url,
        }
    )

    return html_message
