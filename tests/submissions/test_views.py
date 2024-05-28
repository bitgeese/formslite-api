import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from web_forms.access_keys.models import AccessKey
from web_forms.submissions.models import Submission


@pytest.mark.django_db
def test_submission_create_view():
    client = APIClient()
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    data = {
        "access_key": str(access_key.id),  # Ensure the UUID is converted to a string
        "field1": "value1",
        "field2": "value2",
    }
    response = client.post(reverse("api:submission-list"), data, format="multipart")
    print(response.status_code)
    assert response.status_code == 302
    assert Submission.objects.count() == 1
    submission = Submission.objects.get()
    assert submission.access_key == access_key
    assert submission.data == {"field1": "value1", "field2": "value2"}


@pytest.mark.django_db
def test_get_submissions_by_access_key():
    client = APIClient()
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    submission = Submission.objects.create(
        access_key=access_key, data={"field1": "value1"}
    )
    url = reverse(
        "api:submission-get-submissions-by-access-key",
        kwargs={"access_key_id": access_key.id},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == submission.id
