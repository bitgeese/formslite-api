from rest_framework import serializers

from web_forms.access_keys.models import AccessKey, SimpleUser


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleUser
        fields = ["email"]


class AccessKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessKey
        fields = ["id", "name", "email"]

    def create(self, validated_data):
        email_data = validated_data.pop("email")
        user_email, created = SimpleUser.objects.get_or_create(**email_data)
        access_key = AccessKey.objects.create(email=user_email, **validated_data)
        return access_key
