import pytest

from web_forms.access_keys.models import AccessKey


@pytest.mark.django_db
def test_access_key_creation():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    assert access_key.name == "Test User"
    assert access_key.email == "test@example.com"


@pytest.mark.django_db
def test_access_key_soft_delete():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    access_key.soft_delete()
    assert not access_key.is_active


@pytest.mark.django_db
def test_access_key_restore():
    access_key = AccessKey.objects.create(
        name="Test User", email="test@example.com", is_active=False
    )
    access_key.restore()
    assert access_key.is_active
