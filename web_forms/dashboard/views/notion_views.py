from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from web_forms.access_keys.models import UserSettings
from web_forms.utils.notion_integration import get_authorization_url, get_access_token

@login_required
def notion_authorize(request):
    authorization_url = get_authorization_url()
    return redirect(authorization_url)

@login_required
def notion_callback(request):
    code = request.GET.get('code')
    token_response = get_access_token(code)
    access_token = token_response.get('access_token')
    bot_id = token_response.get('bot_id')  # Optional: capture other response fields as needed

    # Save the access token to the user's profile
    profile = request.user.profile
    profile.notion_token = access_token
    profile.notion_bot_id = bot_id  # Optional
    profile.save()
    
    return redirect('profile')
