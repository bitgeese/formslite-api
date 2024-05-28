from rest_framework import serializers

from web_forms.access_keys.models import AccessKey
from web_forms.submissions.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    access_key = serializers.CharField(write_only=True)
    data = serializers.JSONField(required=False)

    class Meta:
        model = Submission
        fields = ["id", "access_key", "data"]
        extra_kwargs = {"access_key": {"write_only": True}}

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

    def create(self, validated_data):
        access_key = validated_data.pop("access_key")
        data = validated_data.pop("data")
        submission = Submission.objects.create(access_key=access_key, data=data)
        return submission

    def to_representation(self, instance):
        """
        Override to_representation to adjust the output of the serialized data.
        Here, we omit the access_key in the output.
        """
        ret = super().to_representation(instance)
        ret.pop("access_key", None)
        return ret
