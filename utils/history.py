from django.utils.translation import gettext_lazy as _

from invoices_app import INVOICE_STATUS
from invoices_app.models import Comment, Invoice


def get_status_display(status):
    for k, v in INVOICE_STATUS:
        if k == status:
            return v


def invoice_history_comments(invoice):
    """
    This function returns a list of automaticly generated comments for an invoice.
    The comments are generated using the invoice change history, this allows us
    to create the comments in the current user's language.

    The comments contain the user that made the change and a text message with every
    field that changed with the original value and the new value.
    """
    history = Invoice.history.filter(id=invoice.id)
    record = history.last()
    comments = []
    while record.next_record:
        next_record = record.next_record
        delta = next_record.diff_against(record)
        message = _('Changed: \n')
        for change in delta.changes:
            if change.field != 'status':
                old_value = change.old
                new_value = change.new
            else:
                old_value = get_status_display(change.old)
                new_value = get_status_display(change.new)
            message += _('{} from {} to {}\n').format(
                Invoice._meta.get_field(change.field).verbose_name,
                old_value,
                new_value,
            )
        comment = Comment(
            user=next_record.history_user,
            invoice=next_record.instance,
            message=message,
            comment_date_received=next_record.history_date
        )
        comments.append(comment)
        record = next_record
    return comments
