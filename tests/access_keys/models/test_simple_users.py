import pytest
from django.core.cache import cache

from web_forms.access_keys.models import SimpleUser


@pytest.mark.django_db
def test_simple_user_creation():
    user = SimpleUser.objects.create(email="test@example.com")
    assert user.email == "test@example.com"
