import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_staff(subject, lines):
    """E-mail the admissions team. Never breaks the form if mail is not configured."""
    recipients = settings.ADMISSIONS_NOTIFY_EMAILS
    if not recipients:
        return
    try:
        send_mail(subject, "\n".join(lines), settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    except Exception:  # noqa: BLE001 - mail problems must not lose the enquiry
        logger.exception("Could not send notification e-mail")
