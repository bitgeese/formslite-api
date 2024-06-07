from typing import Optional

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from web_forms.access_keys.models import SimpleUser


def send_sign_in_email(user: SimpleUser) -> None:
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"https://api.formslite.io/verify-email/{uid}/{token}/"
    reverse(
        "dashboard:verify_email", kwargs={"uidb64": uid, "token": token}
    )

    subject = "Your login link ⚡️"
    message = (
        "Hi there 🙂\n"
        "Please click "
        f'<a href="{verification_link}" target="_blank">here</a> '
        "to verify your email address"
    )
    send_mail(subject, "", settings.EMAIL_HOST_USER, [user.email], html_message=message)


def decode_uid(uidb64: str) -> Optional[str]:
    """Decode the base64 encoded UID."""
    try:
        return urlsafe_base64_decode(uidb64).decode()
    except (TypeError, ValueError, OverflowError):
        return None


def get_user_by_uid(uid: str) -> Optional[SimpleUser]:
    """Retrieve user object using UID."""
    try:
        return SimpleUser.objects.get(pk=uid)
    except SimpleUser.DoesNotExist:
        return None
