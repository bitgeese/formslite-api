from django.conf import settings
from rest_framework import serializers

from web_forms.access_keys.models import AccessKey
from web_forms.submissions.utils.spam_detection import is_spam
from web_forms.utils.emails import send_usage_limit_reached_email

from ..models import Submission as SubmissionAnalytics
from .fields import SemicolonSeparatedEmailField


class SubmissionSerializer(serializers.Serializer):
    access_key = serializers.CharField()
    redirect = serializers.URLField(default=settings.SUBMISSION_SUCCESS_URL)
    from_name = serializers.CharField(required=False)
    reply_to = serializers.EmailField(required=False)
    cc_emails = SemicolonSeparatedEmailField(required=False, write_only=True)
    data = serializers.JSONField(required=False)

    def validate_access_key(self, value):
        try:
            access_key = AccessKey.objects.get(id=value, is_active=True)
        except AccessKey.DoesNotExist:
            raise serializers.ValidationError("Invalid access key provided")
        if access_key.usage_limit_exceeded:
            send_usage_limit_reached_email(access_key)
            raise serializers.ValidationError("Usage limit exceeded for key provided")
        return access_key

    def validate(self, data):
        data_field = {k: v for k, v in self.initial_data.items() if k != "access_key"}
        if is_spam(data_field):
            SubmissionAnalytics.objects.create(
                access_key=data["access_key"], is_spam=True
            )
            raise serializers.ValidationError("Submission flagged as spam")
        if not data_field:
            raise serializers.ValidationError("Submission has no fields")
        data["data"] = data_field
        SubmissionAnalytics.objects.create(access_key=data["access_key"])
        return data
