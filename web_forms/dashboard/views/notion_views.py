from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

import web_forms.utils.notion_integration as notion_auth


@login_required
def notion_authorize(request):
    authorization_url = notion_auth.get_authorization_url()
    return redirect(authorization_url)


@login_required
def notion_callback(request):
    code = request.GET.get("code")
    token_response = notion_auth.get_access_token(code)
    access_token = token_response.get("access_token")
    settings = request.user.settings
    settings.notion_token = access_token
    settings.save()

    return redirect("dashboard:home")
