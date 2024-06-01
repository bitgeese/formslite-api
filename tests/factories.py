import uuid

from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from web_forms.access_keys.models import AccessKey


class SimpleUserFactory(DjangoModelFactory):
    email = Faker("email")

    class Meta:
        model = AccessKey
        django_get_or_create = ["email"]


class AccessKeyFactory(DjangoModelFactory):
    id = uuid.uuid4
    email = SubFactory(SimpleUserFactory, email="email")
    name = Faker("name")

    class Meta:
        model = AccessKey
        django_get_or_create = ["email"]
