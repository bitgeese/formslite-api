import pytest
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_submission_view_success(api_client, access_key):
    """Test the SubmissionView with valid data."""
    url = reverse("api:submission")
    data = {"access_key": access_key.id, "field1": "value1", "field2": "value2"}
    response = api_client.post(url, data, format="multipart")

    assert response.status_code == status.HTTP_302_FOUND

    # Check that an email was sent
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.subject == "New Submission Received"
    assert email.to == [access_key.email]
    assert "Access Key: {}".format(access_key.id) in email.body
    assert "<li><strong>Field1:</strong> value1</li>" in email.body
    assert "<li><strong>Field2:</strong> value2</li>" in email.body


@pytest.mark.django_db
def test_submission_view_invalid_access_key(api_client):
    """Test the SubmissionView with an invalid access key."""
    url = reverse("api:submission")
    data = {"access_key": "invalid_key", "field1": "value1", "field2": "value2"}
    response = api_client.post(url, data, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "access_key" in response.data


@pytest.mark.django_db
def test_submission_view_missing_access_key(api_client):
    """Test the SubmissionView with missing access key."""
    url = reverse("api:submission")
    data = {"field1": "value1", "field2": "value2"}
    response = api_client.post(url, data, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "access_key" in response.data


@pytest.mark.django_db
def test_submission_view_with_extra_fields(api_client, access_key):
    """Test the SubmissionView with extra fields in data."""
    url = reverse("api:submission")
    data = {
        "access_key": access_key.id,
        "extra_field1": "extra_value1",
        "extra_field2": "extra_value2",
    }
    response = api_client.post(url, data, format="multipart")

    assert response.status_code == status.HTTP_302_FOUND

    # Check that an email was sent
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.subject == "New Submission Received"
    assert email.to == [access_key.email]
    assert "Access Key: {}".format(access_key.id) in email.body
    assert "<li><strong>Extra Field1:</strong> extra_value1</li>" in email.body
    assert "<li><strong>Extra Field2:</strong> extra_value2</li>" in email.body
