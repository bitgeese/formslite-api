import pytest

from web_forms.access_keys.api.serializers import AccessKeySerializer
from web_forms.access_keys.models import AccessKey


@pytest.mark.django_db
def test_access_key_serializer(simple_user):
    access_key = AccessKey(name="Test User", user=simple_user)
    serializer = AccessKeySerializer(instance=access_key)
    print(serializer.data)
    assert serializer.data == {
        "id": str(access_key.id),
        "name": "Test User",
        "user": simple_user.email,
    }


@pytest.mark.django_db
def test_access_key_serializer_validation(simple_user):
    data = {"name": "Test User", "user": simple_user.email}
    serializer = AccessKeySerializer(data=data)
    assert serializer.is_valid()
    assert serializer.validated_data == {"name": "Test User", "user": simple_user}
