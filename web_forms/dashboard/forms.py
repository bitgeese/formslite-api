from django import forms

from web_forms.access_keys.models import NotionLink, UserSettings


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


class NotionLinkForm(forms.ModelForm):
    class Meta:
        model = NotionLink
        fields = ["database_id", "database_name", "access_key"]


class WhitelistedDomainForm(forms.ModelForm):
    whitelisted_domains = forms.CharField(
        widget=forms.Textarea, help_text="Enter one domain per line."
    )

    class Meta:
        model = UserSettings
        fields = ["whitelisted_domains"]

    def clean_domains(self):
        domains = self.cleaned_data["whitelisted_domains"]
        domain_list = domains.splitlines()
        return "\n".join(domain.strip() for domain in domain_list if domain.strip())
