import pytest

from tests.submissions.factories import AccessKeyFactory
from web_forms.access_keys.models import AccessKey


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture()
def access_key(db) -> AccessKey:
    return AccessKeyFactory()
