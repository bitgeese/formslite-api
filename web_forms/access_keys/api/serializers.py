from rest_framework import serializers

from web_forms.access_keys.models import AccessKey, SimpleUser


class EmailRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.email

    def to_internal_value(self, data):
        try:
            user_email, created = SimpleUser.objects.get_or_create(email=data)
            return user_email
        except SimpleUser.DoesNotExist:
            raise serializers.ValidationError("User email does not exist")


class AccessKeySerializer(serializers.ModelSerializer):
    user = EmailRelatedField(queryset=SimpleUser.objects.all())

    class Meta:
        model = AccessKey
        fields = ["id", "name", "user"]

    def create(self, validated_data):
        user = validated_data.pop("user")
        access_key = AccessKey.objects.create(user=user, **validated_data)
        return access_key
