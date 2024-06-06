from rest_framework import serializers


class SemicolonSeparatedEmailField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            error_message = "This field must be a string."
            raise serializers.ValidationError(error_message)

        email_list = [email.strip() for email in data.split(";") if email.strip()]

        for email in email_list:
            if not serializers.EmailField().run_validation(email):
                error_message = f"Invalid email address: {email}"
                raise serializers.ValidationError(error_message)

        return email_list

    def to_representation(self, value):
        if not isinstance(value, list):
            error_message = "This field must be a list."
            raise serializers.ValidationError(error_message)
        return ";".join([x.strip() for x in value])
