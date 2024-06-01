import json
from unittest.mock import patch

import pytest
import stripe
from django.conf import settings
from django.urls import reverse

from web_forms.access_keys.models import PlanEnum, SimpleUser


@pytest.fixture
def client():
    from django.test import Client

    return Client()


@pytest.fixture
def stripe_webhook_url():
    return reverse("api:billing-webhook")


@pytest.fixture
def stripe_webhook_secret():
    return settings.STRIPE_WEBHOOK_SECRET


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_invoice_payment_succeeded(mock_construct_event, client, stripe_webhook_url):
    payload = {
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "subscription": "sub_12345",
                "customer_email": "test@example.com",
            }
        },
    }
    mock_construct_event.return_value = payload

    response = client.post(
        stripe_webhook_url,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="mocked_signature",
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    user = SimpleUser.objects.get(email="test@example.com")
    assert user.plan == PlanEnum.PLUS.value
    assert user.stripe_subscription_id == "sub_12345"


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_invoice_payment_failed(mock_construct_event, client, stripe_webhook_url):
    # Create a user first
    user = SimpleUser.objects.create(email="test@example.com", plan=PlanEnum.PLUS.value)

    payload = {
        "type": "invoice.payment_failed",
        "data": {"object": {"customer_email": "test@example.com"}},
    }
    mock_construct_event.return_value = payload

    response = client.post(
        stripe_webhook_url,
        data=json.dumps(payload),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="mocked_signature",
    )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    user.refresh_from_db()
    assert user.plan == PlanEnum.FREE.value


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_invalid_signature(mock_construct_event, client, stripe_webhook_url):
    mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
        "Invalid signature", "header"
    )

    response = client.post(
        stripe_webhook_url,
        data=json.dumps({}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="invalid_signature",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid signature"}


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
def test_invalid_payload(mock_construct_event, client, stripe_webhook_url):
    mock_construct_event.side_effect = ValueError("Invalid payload")

    response = client.post(
        stripe_webhook_url,
        data=json.dumps({}),
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="mocked_signature",
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid payload"}
