from rest_framework import serializers


class SemicolonSeparatedEmailField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            raise serializers.ValidationError("This field must be a string.")

        email_list = [email.strip() for email in data.split(";") if email.strip()]

        for email in email_list:
            if not serializers.EmailField().run_validation(email):
                raise serializers.ValidationError(f"Invalid email address: {email}")

        return email_list

    def to_representation(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("This field must be a list.")
        return ";".join([x.strip() for x in value])
