from django.urls import path

# from .views import admin as admin_views
from .views import client as client_views
from .views import notion_views

app_name = "dashboard"
urlpatterns = [
    path("", client_views.home, name="home"),
    path("login/", client_views.SendSignInEmail.as_view(), name="sign_in"),
    path("logout/", client_views.logout, name="sign_out"),
    path(
        "verify-email/<uidb64>/<token>/", client_views.verify_email, name="verify_email"
    ),
    path("whitelist/", client_views.domain_whitelist, name="whitelist"),
    # Notion integration
    path("notion/authorize/", notion_views.notion_authorize, name="notion_authorize"),
    path("notion/callback/", notion_views.notion_callback, name="notion_callback"),
    path("notion/addLink/", client_views.add_notion_link, name="notion_add"),
]
