from rest_framework import serializers

from web_forms.access_keys.models import AccessKey
from web_forms.submissions.utils.spam_detection import is_spam


class SubmissionSerializer(serializers.Serializer):
    access_key = serializers.CharField()
    data = serializers.JSONField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs["context"].get("request")
        super(SubmissionSerializer, self).__init__(*args, **kwargs)

    def validate_access_key(self, value):
        try:
            access_key = AccessKey.objects.get(id=value, is_active=True)
        except AccessKey.DoesNotExist:
            raise serializers.ValidationError("Invalid access key provided")
        if access_key.usage_limit_exceeded:
            raise serializers.ValidationError("Usage limit exceeded for key provided")
        return access_key

    def validate(self, data):
        data_field = {k: v for k, v in self.initial_data.items() if k != "access_key"}
        if is_spam(data_field):
            raise serializers.ValidationError("Submission flagged as spam")
        data["data"] = data_field
        return data
