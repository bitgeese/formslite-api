import pytest
from rest_framework.test import APIRequestFactory

from web_forms.authentication import CsrfExemptSessionAuthentication


@pytest.mark.django_db
def test_enforce_csrf():
    factory = APIRequestFactory()
    request = factory.get("/some-url/")

    auth = CsrfExemptSessionAuthentication()

    result = auth.enforce_csrf(request)

    assert result is None
