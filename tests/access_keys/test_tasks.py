import pytest
from django.core.cache import cache

from web_forms.access_keys.models import AccessKey
from web_forms.access_keys.tasks import reset_access_key_usage


@pytest.mark.django_db
def test_reset_access_key_usage(simple_user):
    # Create active AccessKey instances
    access_key1 = AccessKey.objects.create(
        name="Key1", user=simple_user, is_active=True
    )
    access_key2 = AccessKey.objects.create(
        name="Key2", user=simple_user, is_active=True
    )
    inactive_key = AccessKey.objects.create(
        name="Key3", user=simple_user, is_active=False
    )

    # Set some usage values in cache
    access_key1.set_usage(150)
    access_key2.set_usage(200)
    inactive_key.set_usage(250)

    # Run the task
    reset_access_key_usage()

    # Check if usage has been reset to 0 for active keys
    assert cache.get(access_key1.cache_key) == 0
    assert cache.get(access_key2.cache_key) == 0

    # Check if usage for inactive key remains unchanged
    assert cache.get(inactive_key.cache_key) == 250
