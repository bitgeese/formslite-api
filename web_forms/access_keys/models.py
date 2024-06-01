import uuid
from enum import Enum

from django.core.cache import cache
from django.db import models

from web_forms.models import BaseModel

USAGE_KEY = "access_key_usage_{access_key_id}"
MONTHLY_USE_LIMIT = 300


class PlanEnum(Enum):
    FREE = "free"
    PLUS = "plus"
    ELITE = "elite"

    @classmethod
    def choices(cls):
        return [(key.value, key.name.title()) for key in cls]


class EmailUser(BaseModel):
    email = models.EmailField()


class AccessKey(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    plan = models.CharField(
        max_length=10, choices=PlanEnum.choices(), default=PlanEnum.FREE.value
    )

    def soft_delete(self):
        self.is_active = False
        self.save()

    def restore(self):
        self.is_active = True
        self.save()

    def use_access_key(self):
        if not cache.has_key(self.cache_key):
            return cache.set(self.cache_key, 1)
        return cache.incr(self.cache_key)

    def reset_usage(self):
        return cache.set(self.cache_key, 0)

    def set_usage(self, usage):
        return cache.set(self.cache_key, usage)

    @property
    def usage_limit_exceeded(self):
        if self.plan == PlanEnum.FREE.value and self.usage >= MONTHLY_USE_LIMIT:
            return True
        return False

    @property
    def usage(self):
        return cache.get(self.cache_key, 0)

    @property
    def cache_key(self):
        return USAGE_KEY.format(access_key_id=self.id)
