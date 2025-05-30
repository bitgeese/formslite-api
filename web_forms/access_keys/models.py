import logging
import uuid
from enum import Enum

import requests
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.cache import cache
from django.db import models

from web_forms.models import BaseModel
from web_forms.utils.emails import send_auto_respond
from web_forms.utils.notion_integration import NotionClient

from .managers import SimpleUserManager

logger = logging.getLogger(__name__)


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
    auto_responder_intro_text = models.TextField(blank=True, default="")
    auto_responder_include_copy = models.BooleanField(default=True)

    whitelisted_domains = models.TextField(blank=True, default="")

    # notion integration settings
    notion_token = models.CharField(max_length=255, blank=True, default="")


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
    stripe_subscription_id = models.CharField(max_length=125, default="", blank=True)
    auto_reply = models.BooleanField(default=False)

    has_verified_email = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = SimpleUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def auto_respond(self, submission_data):
        if self.is_paid and self.auto_reply:
            logger.info("Sending auto-respond email to user: %s", self.email)
            send_auto_respond(submission_data, self.settings)

    def upgrade_to_plus_plan(self):
        if self.plan != self.PlanEnum.PLUS.value:
            logger.info("Upgrading user %s to PLUS plan", self.email)
            self.plan = self.PlanEnum.PLUS.value
            self.save()

    def __str__(self):
        return self.email

    @property
    def is_paid(self):
        return self.plan != self.PlanEnum.FREE.value

    @property
    def notion_client(self):
        return NotionClient(token=self.settings.notion_token)

    def is_domain_whitelisted(self, domain):
        whitelisted_domains = self.settings.whitelisted_domains.split("\n")
        if self.is_paid and whitelisted_domains:
            logger.info(
                "Checking if domain %s is whitelisted for user %s", domain, self.email
            )
            return domain in whitelisted_domains
        return True


class AccessKey(BaseModel):
    MONTHLY_USE_LIMIT = 300
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=125, default="Access Key")
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
            logger.info("Setting initial usage for access key %s", self.id)
            return cache.set(self.cache_key, 1)
        logger.info("Incrementing usage for access key %s", self.id)
        return cache.incr(self.cache_key)

    def reset_usage(self):
        logger.info("Resetting usage for access key %s", self.id)
        return cache.set(self.cache_key, 0)

    def set_usage(self, usage):
        logger.info("Setting usage to %s for access key %s", usage, self.id)
        return cache.set(self.cache_key, usage)

    @property
    def usage_limit_exceeded(self):
        if (
            self.user.plan == SimpleUser.PlanEnum.FREE.value
            and self.usage >= self.MONTHLY_USE_LIMIT
        ):
            logger.warning("Usage limit exceeded for access key %s", self.id)
            return True
        return False

    @property
    def usage(self):
        return cache.get(self.cache_key, 0)

    @property
    def cache_key(self):
        return USAGE_KEY.format(access_key_id=self.id)

    def send_to_notion(self, submission_data):
        if self.user.is_paid and self.user.settings.notion_token:
            for link in self.notion_links.all():
                logger.info("Sending data to Notion for access key %s", self.id)
                self.user.notion_client.add_row_to_database(
                    database_id=link.database_id,
                    data=submission_data,
                )

    def send_to_webhook(self, submission_data):
        webhook_url = submission_data.pop("webhook", None)
        if self.user.is_paid and webhook_url:
            logger.info("Sending data to webhook for access key %s", self.id)
            response = requests.post(webhook_url, data=submission_data)
            if response.status_code == 200:
                logger.info(
                    "Successfully sent data to webhook for access key %s", self.id
                )
                return True
            else:
                logger.error(
                    "Failed to send data to webhook for access key %s. Status code: %s",
                    self.id,
                    response.status_code,
                )

    def __str__(self):
        return f"{self.name} ({self.id})"


class NotionLink(models.Model):
    user = models.ForeignKey(
        SimpleUser, on_delete=models.CASCADE, related_name="notion_links"
    )
    database_id = models.CharField(max_length=125)
    database_name = models.CharField(max_length=125)
    access_key = models.ForeignKey(
        AccessKey, on_delete=models.CASCADE, related_name="notion_links"
    )

    def __str__(self):
        return f"{self.database_name} - {self.access_key.id}"
