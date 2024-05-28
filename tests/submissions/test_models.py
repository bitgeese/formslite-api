import pytest

from web_forms.access_keys.models import AccessKey
from web_forms.submissions.models import Submission


@pytest.mark.django_db
def test_submission_creation():
    access_key = AccessKey.objects.create(name="Test User", email="test@example.com")
    data = {"field1": "value1"}
    submission = Submission.objects.create(access_key=access_key, data=data)
    assert submission.access_key == access_key
    assert submission.data == data
