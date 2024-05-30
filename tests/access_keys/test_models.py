import pytest
from django.core.cache import cache

from web_forms.access_keys.models import MONTHLY_USE_LIMIT, AccessKey


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


@pytest.mark.django_db
def test_access_key_use():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    assert cache.get(access_key.cache_key) is None

    access_key.use_access_key()
    assert cache.get(access_key.cache_key) == 1


@pytest.mark.django_db
def test_access_key_usage_increment():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    assert cache.get(access_key.cache_key) is None

    access_key.use_access_key()
    access_key.use_access_key()
    assert cache.get(access_key.cache_key) == 2


@pytest.mark.django_db
def test_access_key_usage_limit_exceeded():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")

    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT - 1)
    assert not access_key.usage_limit_exceeded

    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT)
    assert access_key.usage_limit_exceeded


@pytest.mark.django_db
def test_access_key_cache_key():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    expected_cache_key = f"access_key_usage_{access_key.id}"
    assert access_key.cache_key == expected_cache_key
