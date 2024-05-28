import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from web_forms.access_keys.models import AccessKey


@pytest.mark.django_db
def test_access_key_create_view():
    client = APIClient()
    data = {"name": "Test User", "email": "test@example.com"}
    response = client.post(reverse("api:accesskey-list"), data, format="json")
    assert response.status_code == 201
    assert AccessKey.objects.count() == 1
    assert AccessKey.objects.get().name == "Test User"
