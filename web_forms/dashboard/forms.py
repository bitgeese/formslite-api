from django import forms

from web_forms.access_keys.models import UserSettings


class MagicSignInForm(forms.Form):
    email = forms.EmailField(required=True)


class AutoRespondSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            "auto_responder_enabled",
            "auto_responder_from_name",
            "auto_responder_subject",
            "auto_responder_intro_text",
            "auto_responder_include_copy",
        ]
