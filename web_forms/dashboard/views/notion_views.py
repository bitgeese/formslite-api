from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from web_forms.utils.notion_integration import get_access_token, get_authorization_url


@login_required
def notion_authorize(request):
    authorization_url = get_authorization_url()
    return redirect(authorization_url)


@login_required
def notion_callback(request):
    code = request.GET.get("code")
    token_response = get_access_token(code)
    print("RESPONSE:", token_response)
    access_token = token_response.get("access_token")
    settings = request.user.settings
    settings.notion_token = access_token
    settings.save()

    return redirect("dashboard:home")
