import pytest

from web_forms.access_keys.models import AccessKey
from web_forms.submissions.api.serializers import SubmissionSerializer
from web_forms.submissions.models import Submission


@pytest.mark.django_db
def test_submission_serializer():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    data = {"field1": "value1", "field2": "value2"}
    submission = Submission.objects.create(access_key=access_key, data=data)
    serializer = SubmissionSerializer(instance=submission)

    expected_data = {
        "id": submission.id,
        "data": data,
    }
    assert serializer.data == expected_data


@pytest.mark.django_db
def test_submission_serializer_validation(access_key):
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    data = {"access_key": str(access_key.id), "field1": "value1", "field2": "value2"}
    serializer = SubmissionSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    validated_data = serializer.validated_data
    assert validated_data["access_key"] == access_key
    assert validated_data["data"] == {"field1": "value1", "field2": "value2"}


@pytest.mark.django_db
def test_submission_serializer_invalid_access_key():
    invalid_access_key_id = "00000000-0000-0000-0000-000000000000"
    data = {"access_key": invalid_access_key_id, "field1": "value1", "field2": "value2"}
    serializer = SubmissionSerializer(data=data)
    assert not serializer.is_valid()
    assert "access_key" in serializer.errors
    assert serializer.errors["access_key"][0] == "Invalid access key provided"
