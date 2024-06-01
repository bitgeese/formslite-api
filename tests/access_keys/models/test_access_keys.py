import pytest
from django.core.cache import cache

from web_forms.access_keys.models import MONTHLY_USE_LIMIT, AccessKey, PlanEnum


@pytest.mark.django_db
def test_access_key_creation(simple_user):
    access_key = AccessKey.objects.create(name="Test User", user=simple_user)
    assert access_key.name == "Test User"
    assert access_key.user.email == simple_user.email


@pytest.mark.django_db
def test_access_key_soft_delete(access_key):
    assert access_key.is_active
    access_key.soft_delete()
    assert not access_key.is_active


@pytest.mark.django_db
def test_access_key_restore(simple_user):
    access_key = AccessKey.objects.create(
        name="Test User", user=simple_user, is_active=False
    )
    access_key.restore()
    assert access_key.is_active


@pytest.mark.django_db
def test_access_key_use(simple_user):
    access_key = AccessKey.objects.create(name="Test User", user=simple_user)
    assert cache.get(access_key.cache_key) is None

    access_key.use_access_key()
    assert cache.get(access_key.cache_key) == 1


@pytest.mark.django_db
def test_access_key_usage_increment(simple_user):
    access_key = AccessKey.objects.create(name="Test User", user=simple_user)
    assert cache.get(access_key.cache_key) is None

    access_key.use_access_key()
    access_key.use_access_key()
    assert cache.get(access_key.cache_key) == 2


@pytest.mark.django_db
def test_access_key_usage_limit_exceeded(simple_user):
    access_key = AccessKey.objects.create(name="Test User", user=simple_user)

    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT - 1)
    assert not access_key.usage_limit_exceeded

    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT)
    assert access_key.usage_limit_exceeded


@pytest.mark.django_db
def test_access_key_cache_key(simple_user):
    access_key = AccessKey.objects.create(name="Test User", user=simple_user)
    expected_cache_key = f"access_key_usage_{access_key.id}"
    assert access_key.cache_key == expected_cache_key


@pytest.mark.django_db
def test_access_key_reset_usage(access_key):
    access_key.use_access_key()
    access_key.use_access_key()
    assert cache.get(access_key.cache_key) == 2

    access_key.reset_usage()
    assert cache.get(access_key.cache_key) == 0


@pytest.mark.django_db
def test_access_key_usage_limit_exceeded_not_triggered_for_plus_user(simple_user):
    access_key = AccessKey.objects.create(
        name="Test User", user=simple_user, plan=PlanEnum.PLUS.value
    )

    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT - 1)
    assert not access_key.usage_limit_exceeded

    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT)
    assert not access_key.usage_limit_exceeded
