import uuid

from django.core.cache import cache
from django.db import models

from web_forms.models import BaseModel

KEY = "access_key_usage_{access_key_id}"
MONTHLY_USE_LIMIT = 300


class AccessKey(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

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

    @property
    def usage_limit_exceeded(self):
        used = cache.get(self.cache_key, 0)
        if used >= MONTHLY_USE_LIMIT:
            return True
        return False

    @property
    def cache_key(self):
        return KEY.format(access_key_id=self.id)
