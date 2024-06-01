from django.urls import path

from web_forms.access_keys.api.views import access_key_create_api
from web_forms.billing.views import stripe_webhook_view
from web_forms.submissions.api.views import submission_view

app_name = "api"
urlpatterns = [
    path("submission/", submission_view, name="submission"),
    path("access_keys/", access_key_create_api, name="access-keys"),
    path("billing/webhook/", stripe_webhook_view, name="billing-webhook"),
]
