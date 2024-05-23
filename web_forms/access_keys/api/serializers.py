from rest_framework import serializers

from web_forms.access_keys.models import AccessKey


class AccessKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessKey
        fields = ["id", "name", "email"]
