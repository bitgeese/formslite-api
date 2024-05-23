from rest_framework import serializers

from web_forms.access_keys.api.serializers import AccessKeySerializer
from web_forms.access_keys.models import AccessKey
from web_forms.submissions.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    access_key = serializers.PrimaryKeyRelatedField(
        queryset=AccessKey.objects.all(), write_only=True
    )
    data = serializers.JSONField(required=False)

    class Meta:
        model = Submission
        fields = ["id", "access_key", "data"]
        extra_kwargs = {"access_key": {"write_only": True}}

    def validate_access_key(self, value):
        # Validate the access_key to ensure it exists
        if not AccessKey.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid access key provided")
        return value

    def create(self, validated_data):
        # Extract access_key from validated data and remove it
        access_key = validated_data.pop("access_key")

        # Remaining data should be treated as the JSON data field
        data = {
            k: v for k, v in self.context["request"].data.items() if k != "access_key"
        }
        submission = Submission.objects.create(access_key=access_key, data=data)
        return submission

    def to_representation(self, instance):
        """
        Override to_representation to adjust the output of the serialized data.
        Here, we omit the access_key in the output.
        """
        ret = super().to_representation(instance)
        # You can choose to remove or alter the representation as needed, here we skip `access_key`
        ret.pop("access_key", None)
        return ret
