import pytest

from web_forms.access_keys.api.serializers import AccessKeySerializer
from web_forms.access_keys.models import AccessKey


@pytest.mark.django_db
def test_access_key_serializer():
    access_key = AccessKey(name="Test User", email="test@example.com")
    serializer = AccessKeySerializer(instance=access_key)
    assert serializer.data == {
        "id": str(access_key.id),
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest.mark.django_db
def test_access_key_serializer_validation():
    data = {"name": "Test User", "email": "test@example.com"}
    serializer = AccessKeySerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == data
