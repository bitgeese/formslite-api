import json
import logging
from unittest.mock import patch

import pytest
import stripe
from django.conf import settings
from django.urls import reverse

from web_forms.access_keys.models import SimpleUser


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
@patch("web_forms.billing.views.StripeWebhookView._send_email")
def test_invoice_payment_succeeded(
    mock_send_email, mock_construct_event, client, stripe_webhook_url
):
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
    assert user.plan == SimpleUser.PlanEnum.PLUS.value
    assert user.stripe_subscription_id == "sub_12345"
    mock_send_email.assert_called_once_with(
        subject="You have PLUS plan",
        message="You have bought/renewed the plus plan. Your access"
        " keys now have access to plus features.",
        recipient_list=[user.email],
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
@patch("web_forms.billing.views.StripeWebhookView._send_email")
def test_invoice_payment_failed(
    mock_send_email, mock_construct_event, client, stripe_webhook_url
):
    # Create a user first
    user = SimpleUser.objects.create(
        email="test@example.com", plan=SimpleUser.PlanEnum.PLUS.value
    )

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
    assert user.plan == SimpleUser.PlanEnum.FREE.value
    mock_send_email.assert_called_once_with(
        subject="PLUS plan renewal failed",
        message="Renewal payment failed, you are now on the free plan."
        " Renew your payment here: <link>",
        recipient_list=[user.email],
    )


@pytest.mark.django_db
@patch("stripe.Webhook.construct_event")
@patch("web_forms.billing.views.StripeWebhookView._send_email")
def test_invoice_payment_failed_user_does_not_exist(
    mock_send_email, mock_construct_event, client, stripe_webhook_url, caplog
):
    payload = {
        "type": "invoice.payment_failed",
        "data": {"object": {"customer_email": "nonexistent@example.com"}},
    }
    mock_construct_event.return_value = payload

    with caplog.at_level(logging.ERROR):
        response = client.post(
            stripe_webhook_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="mocked_signature",
        )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    # Ensure no email is sent since user does not exist
    mock_send_email.assert_not_called()
    # Ensure the logger captured the error
    assert any(
        "User with email nonexistent@example.com does not exist" in message
        for message in caplog.messages
    )


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
    assert response.json() == {"error": "Invalid event"}


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
    assert response.json() == {"error": "Invalid event"}
