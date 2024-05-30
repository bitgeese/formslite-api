import pytest
from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from web_forms.access_keys.models import MONTHLY_USE_LIMIT
from web_forms.submissions.api.serializers import SubmissionSerializer
from web_forms.submissions.utils.spam_detection import HONEYPOT_FIELD


@pytest.mark.django_db
def test_submission_serializer_valid_access_key(access_key):
    """Test that the serializer is valid with a correct access key."""
    valid_data = {
        "access_key": str(access_key.id),
        "field1": "value1",
        "field2": "value2",
    }
    serializer = SubmissionSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["access_key"] == access_key
    assert "data" in serializer.validated_data
    assert serializer.validated_data["data"]["field1"] == "value1"
    assert serializer.validated_data["data"]["field2"] == "value2"


@pytest.mark.django_db
def test_submission_serializer_invalid_access_key():
    """Test that the serializer raises an error with an invalid access key."""
    invalid_data = {
        "access_key": "d3be4098-5a37-4352-81e3-0d8855462b32",
        "field1": "value1",
        "field2": "value2",
    }
    serializer = SubmissionSerializer(data=invalid_data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    print(excinfo.value)
    assert "Invalid access key provided" in str(excinfo.value)


@pytest.mark.django_db
def test_submission_serializer_access_key_disabled(access_key):
    """Test that the serializer raises an error
    when access key is disabled."""
    access_key.soft_delete()
    invalid_data = {
        "access_key": str(access_key.id),
        "field1": "value1",
        "field2": "value2",
    }
    serializer = SubmissionSerializer(data=invalid_data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    assert "Invalid access key provided" in str(excinfo.value)


@pytest.mark.django_db
def test_submission_serializer_spam_detected_honypot(access_key):
    """Test that the serializer raises an error
    when spam is submited"""
    invalid_data = {
        "access_key": str(access_key.id),
        HONEYPOT_FIELD: "tuntenoeu",
        "field1": "value1",
        "field2": "value2",
    }
    serializer = SubmissionSerializer(data=invalid_data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    assert "Submission flagged as spam" in str(excinfo.value)


@pytest.mark.django_db
def test_submission_serializer_usage_limit_exceeded(access_key):
    """Test that the serializer raises an error
    when access key usage limit is exceeded."""
    cache.set(access_key.cache_key, MONTHLY_USE_LIMIT)
    invalid_data = {
        "access_key": str(access_key.id),
        "field1": "value1",
        "field2": "value2",
    }
    serializer = SubmissionSerializer(data=invalid_data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    assert "Usage limit exceeded for key provided" in str(excinfo.value)


@pytest.mark.django_db
def test_submission_serializer_missing_access_key():
    """Test that the serializer raises an error when access key is missing."""
    missing_key_data = {"field1": "value1", "field2": "value2"}
    serializer = SubmissionSerializer(data=missing_key_data)
    assert not serializer.is_valid()
    assert "access_key" in serializer.errors


@pytest.mark.django_db
def test_submission_serializer_no_data(access_key):
    """Test that the serializer is valid when the data field is omitted."""
    invalid_data = {"access_key": str(access_key.id)}
    serializer = SubmissionSerializer(data=invalid_data)
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)
    assert "Submission has no fields" in str(excinfo.value)


@pytest.mark.django_db
def test_submission_serializer_with_extra_fields(access_key):
    """Test that the serializer correctly includes additional fields in data."""
    valid_data = {
        "access_key": str(access_key.id),
        "extra_field1": "extra_value1",
        "extra_field2": "extra_value2",
    }
    serializer = SubmissionSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["access_key"] == access_key
    assert "data" in serializer.validated_data
    assert serializer.validated_data["data"]["extra_field1"] == "extra_value1"
    assert serializer.validated_data["data"]["extra_field2"] == "extra_value2"
