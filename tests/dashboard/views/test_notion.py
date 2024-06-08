from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse

from web_forms.access_keys.models import SimpleUser


@pytest.fixture
def user(db):
    user = SimpleUser.objects.create_user(
        email="testuser@test.com", password="testpassword"
    )
    return user


@pytest.fixture
def authenticated_client(user):
    client = Client()
    client.login(email="testuser@test.com", password="testpassword")
    return client


@pytest.mark.django_db
@patch("web_forms.utils.notion_integration.get_authorization_url")
def test_notion_authorize(mock_get_authorization_url, authenticated_client):
    mock_get_authorization_url.return_value = "https://notion.example.com/authorize"

    response = authenticated_client.get(reverse("dashboard:notion_authorize"))

    assert response.status_code == 302
