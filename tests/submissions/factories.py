import uuid

from factory import Faker
from factory.django import DjangoModelFactory

from web_forms.submissions.models import AccessKey


class AccessKeyFactory(DjangoModelFactory):
    id = uuid.uuid4
    email = Faker("email")
    name = Faker("name")

    class Meta:
        model = AccessKey
        django_get_or_create = ["email"]
