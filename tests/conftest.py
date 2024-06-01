import pytest
from rest_framework.test import APIClient

from tests.factories import AccessKeyFactory, SimpleUserFactory
from web_forms.access_keys.models import AccessKey, SimpleUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture()
def access_key(db) -> AccessKey:
    return AccessKeyFactory()


@pytest.fixture()
def simple_user(db) -> SimpleUser:
    return SimpleUserFactory()
