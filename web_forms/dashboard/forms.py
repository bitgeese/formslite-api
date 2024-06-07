from django import forms


class MagicSignInForm(forms.Form):
    email = forms.EmailField(required=True)
