import pytest

from web_forms.access_keys.models import SimpleUser, PlanEnum


@pytest.mark.django_db
def test_simple_user_creation():
    user = SimpleUser.objects.create(email="test@example.com")
    assert user.email == "test@example.com"


@pytest.mark.django_db
def test_simple_user_upgrade_plus_plan(simple_user):
    assert simple_user.plan == PlanEnum.FREE.value

    simple_user.upgrade_to_plus_plan()

    assert simple_user.plan == PlanEnum.PLUS.value