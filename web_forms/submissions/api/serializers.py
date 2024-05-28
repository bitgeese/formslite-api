from rest_framework import serializers

from web_forms.access_keys.models import AccessKey


class SubmissionSerializer(serializers.Serializer):
    access_key = serializers.CharField()
    data = serializers.JSONField(required=False)

    def validate_access_key(self, value):
        try:
            access_key = AccessKey.objects.get(id=value)
        except AccessKey.DoesNotExist:
            raise serializers.ValidationError("Invalid access key provided")
        return access_key

    def validate(self, data):
        data_field = {k: v for k, v in self.initial_data.items() if k != "access_key"}
        data["data"] = data_field
        return data
