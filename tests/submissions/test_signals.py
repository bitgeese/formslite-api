import pytest
from django.conf import settings
from django.core import mail

from web_forms.access_keys.models import AccessKey


@pytest.mark.django_db
def test_send_access_key_created_email_to_admin(simple_user):
    assert len(mail.outbox) == 0

    access_key = AccessKey.objects.create(user=simple_user, name="test")

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.subject == "New AccessKey Created"
    assert settings.ADMINS[0][1] in email.to
    assert f"Access Key: {access_key.id}" in email.body
