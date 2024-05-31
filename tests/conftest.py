import pytest
from rest_framework.test import APIClient

from tests.submissions.factories import AccessKeyFactory
from web_forms.access_keys.models import AccessKey


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture()
def access_key(db) -> AccessKey:
    return AccessKeyFactory()
