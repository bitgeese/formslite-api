import base64
import json
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from django.conf import settings
from django.urls import reverse_lazy

import web_forms.utils.notion_integration as notion_auth

REDIRECT_URI = reverse_lazy("dashboard:notion_callback")


@pytest.fixture
def settings_override(settings):
    settings.NOTION_CLIENT_ID = "test_client_id"
    settings.NOTION_CLIENT_SECRET = "test_client_secret"
    settings.NOTION_AUTHORIZATION_URL = "https://notion.example.com/authorize"
    settings.NOTION_TOKEN_URL = "https://notion.example.com/token"
    return settings


def test_get_authorization_url(settings_override):
    params = {
        "client_id": settings_override.NOTION_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "database.read database.write",
    }
    assert (
        notion_auth.get_authorization_url()
        == f"{settings.NOTION_AUTHORIZATION_URL}?{urlencode(params)}"
    )


@patch("requests.post")
def test_get_access_token(mock_post, settings_override):
    code = "test_code"
    expected_token = {"access_token": "test_access_token"}

    mock_response = mock_post.return_value
    mock_response.raise_for_status = lambda: None
    mock_response.json.return_value = expected_token

    result = notion_auth.get_access_token(code)

    assert result == expected_token

    credentials = (
        f"{settings_override.NOTION_CLIENT_ID}:{settings_override.NOTION_CLIENT_SECRET}"
    )
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    expected_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_credentials}",
    }
    expected_data = json.dumps(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"https://api.formslite.io{REDIRECT_URI}",
        }
    )

    mock_post.assert_called_once_with(
        "https://notion.example.com/token", data=expected_data, headers=expected_headers
    )
