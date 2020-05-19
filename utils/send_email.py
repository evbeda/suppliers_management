from typing import Tuple, List

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.translation import (
    ugettext_lazy as _,
)
from django.contrib import messages
from supplier_app.constants.custom_messages import EMAIL_ERROR_MESSAGE
from supplier_app.models import (
    CompanyUserPermission,
    TaxPayer,
    InvitingBuyer)
from supplier_app.constants.email_notifications import email_notifications
from celery import shared_task
from utils import GO_TO_BRITESU
from utils.exceptions import CouldNotSendEmailError
from supplier_app.constants.email_notifications import (
    SUPPLIER_HOME_URL,
)
from django.utils.translation import to_locale, get_language


@shared_task(ignore_result=True)
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
    subject = _(email_notifications['company_invitation']['subject'])
    upper_text = _(email_notifications['company_invitation']['body']['upper_text'])
    lower_text = _(email_notifications['company_invitation']['body']['lower_text'])
    disclaimer = _(email_notifications['company_invitation']['body']['disclaimer'])
    btn_text = _(email_notifications['company_invitation']['body']['btn_text'])
    btn_url = email_notifications['company_invitation']['body']['btn_url']
    message = build_mail_html(
        company.name,
        upper_text,
        lower_text,
        disclaimer,
        btn_text,
        '{}/{}'.format(btn_url, token),
    )
    send_email_notification.apply_async([subject, message, email])


def get_message_and_subject(change_type: str, taxpayer: TaxPayer) -> Tuple[str, str]:
    subject = _(email_notifications[change_type]['subject'])
    upper_text = _(email_notifications[change_type]['body']['upper_text'])
    lower_text = _(email_notifications[change_type]['body']['lower_text'])
    disclaimer = _(email_notifications['company_invitation']['body']['disclaimer'])
    btn_text = _(email_notifications[change_type]['body']['btn_text'])
    btn_url = email_notifications[change_type]['body']['btn_url']
    message = build_mail_html(
        taxpayer.business_name,
        upper_text,
        lower_text,
        disclaimer,
        btn_text,
        btn_url,
    )
    return message, subject


def get_supplier_language_by_taxpayer(taxpayer):
    company_id = TaxPayer.objects.get(pk=taxpayer.id).company.id
    supplier_language = CompanyUserPermission.objects.filter(company_id=company_id).order_by('user_id').reverse()[0].user.preferred_language
    return supplier_language


def taxpayer_notification(taxpayer, change_type):
    taxpayer_language = to_locale(get_language())
    translation.activate(get_supplier_language_by_taxpayer(taxpayer))
    message, subject = get_message_and_subject(change_type, taxpayer)
    recipient_list = get_user_emails_by_tax_payer_id(taxpayer.id)
    send_email_notification.apply_async([subject, message, recipient_list])
    translation.activate(taxpayer_language)


def buyer_notification(taxpayer, change_type):
    message, subject = get_message_and_subject(change_type, taxpayer)
    recipient_list = get_buyer_emails_by_tax_payer_id(taxpayer.id)
    send_email_notification.apply_async([subject, message, recipient_list])


def get_user_emails_by_tax_payer_id(tax_payer_id):
    company = TaxPayer.objects.get(pk=tax_payer_id).company
    emails = CompanyUserPermission.objects.values_list(
        'user__email',
        flat=True,
    ).filter(company=company)
    return list(emails)


def get_buyer_emails_by_tax_payer_id(tax_payer_id: int) -> List[str]:
    company = TaxPayer.objects.get(pk=tax_payer_id).company
    buyer = InvitingBuyer.objects.get(company=company.id).inviting_buyer
    return [buyer.email]


def build_mail_html(
    supplier_name,
    upper_text,
    lower_text,
    disclaimer,
    btn_text=GO_TO_BRITESU,
    btn_url='{}{}'.format(settings.BRITESU_BASE_URL, SUPPLIER_HOME_URL)
):
    html_message = render_to_string(
        'mail_template.html',
        {
            'supplier_name': supplier_name,
            'upper_text': upper_text,
            'lower_text': lower_text,
            'disclaimer': disclaimer,
            'btn_text': btn_text,
            'btn_url': btn_url,
        }
    )

    return html_message
