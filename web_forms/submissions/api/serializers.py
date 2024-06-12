import logging

from django.conf import settings
from rest_framework import serializers

from web_forms.access_keys.models import AccessKey
from web_forms.utils.emails import send_usage_limit_reached_email

from .fields import SemicolonSeparatedEmailField

logger = logging.getLogger(__name__)


class SubmissionSerializer(serializers.Serializer):
    access_key = serializers.CharField()
    redirect = serializers.URLField(default=settings.SUBMISSION_SUCCESS_URL)
    from_name = serializers.CharField(required=False)
    reply_to = serializers.EmailField(required=False)
    cc_emails = SemicolonSeparatedEmailField(required=False, write_only=True)
    data = serializers.JSONField(required=False)

    def validate_access_key(self, value):
        logger.info("Validating access key: %s", value)
        try:
            access_key = AccessKey.objects.get(id=value, is_active=True)
        except AccessKey.DoesNotExist:
            logger.warning("Invalid access key provided: %s", value)
            raise serializers.ValidationError("Invalid access key provided")
        if access_key.usage_limit_exceeded:
            logger.info("Usage limit exceeded for access key: %s", value)
            send_usage_limit_reached_email(access_key)
            raise serializers.ValidationError("Usage limit exceeded for key provided")

        logger.info("Access key validated: %s", value)
        return access_key

    def validate(self, data):
        data_field = {k: v for k, v in self.initial_data.items() if k != "access_key"}
        if not data_field:
            logger.warning("Submission has no fields: %s", data)
            raise serializers.ValidationError("Submission has no fields")
        data["data"] = data_field
        logger.info("Submission data validated: %s", data)
        return data
