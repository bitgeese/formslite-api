import uuid
from enum import Enum

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.cache import cache
from django.db import models

from web_forms.models import BaseModel
from web_forms.utils.emails import send_auto_respond

from .managers import SimpleUserManager

USAGE_KEY = "access_key_usage_{access_key_id}"


class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="settings"
    )

    # auto responder settings
    auto_responder_enabled = models.BooleanField(default=False)
    auto_responder_from_name = models.CharField(
        max_length=125, default="Your Company Name"
    )
    auto_responder_subject = models.CharField(
        max_length=125, default="Auto Responder Email Subject"
    )
    auto_responder_intro_text = models.TextField(null=True, blank=True, default="")
    auto_responder_include_copy = models.BooleanField(default=True)


class SimpleUser(AbstractBaseUser, PermissionsMixin):
    class PlanEnum(Enum):
        FREE = "free"
        PLUS = "plus"
        ELITE = "elite"

        @classmethod
        def choices(cls):
            return [(key.value, key.name.title()) for key in cls]

    email = models.EmailField(unique=True)
    plan = models.CharField(
        max_length=10, choices=PlanEnum.choices(), default=PlanEnum.FREE.value
    )
    stripe_subscription_id = models.CharField(
        unique=True, max_length=125, null=True, blank=True
    )
    auto_reply = models.BooleanField(default=False)

    has_verified_email = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = SimpleUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def auto_respond(self, submission_data):
        if self.plan != self.PlanEnum.FREE.value and self.auto_reply:
            send_auto_respond(submission_data, self.settings)

    def upgrade_to_plus_plan(self):
        if self.plan != self.PlanEnum.PLUS.value:
            self.plan = self.PlanEnum.PLUS.value
            self.save()

    def __str__(self):
        return self.email


class AccessKey(BaseModel):
    MONTHLY_USE_LIMIT = 300
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125)
    user = models.ForeignKey(SimpleUser, on_delete=models.CASCADE, related_name="keys")
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

    def reset_usage(self):
        return cache.set(self.cache_key, 0)

    def set_usage(self, usage):
        return cache.set(self.cache_key, usage)

    @property
    def usage_limit_exceeded(self):
        if (
            self.user.plan == SimpleUser.PlanEnum.FREE.value
            and self.usage >= self.MONTHLY_USE_LIMIT
        ):
            return True
        return False

    @property
    def usage(self):
        return cache.get(self.cache_key, 0)

    @property
    def cache_key(self):
        return USAGE_KEY.format(access_key_id=self.id)
