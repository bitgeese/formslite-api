import logging

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from web_forms.access_keys.models import PlanEnum, SimpleUser

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        event = self._construct_event(payload, sig_header, endpoint_secret)
        if not event:
            return JsonResponse({"error": "Invalid event"}, status=400)

        logger.info(f"Received event: {event['type']}")

        event_handlers = {
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
        }

        handler = event_handlers.get(event["type"])
        if handler:
            handler(event)

        return JsonResponse({"status": "success"}, status=200)

    def _construct_event(self, payload, sig_header, endpoint_secret):
        try:
            return stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error(f"Error constructing event: {str(e)}")
            return None

    def _handle_payment_succeeded(self, event):
        invoice = event["data"]["object"]
        logger.info(f"Invoice: {invoice}")
        email = invoice.get("customer_email")
        subscription_id = invoice.get("subscription")

        if email:
            simple_user, _ = SimpleUser.objects.get_or_create(email=email)
            simple_user.plan = PlanEnum.PLUS.value
            simple_user.stripe_subscription_id = subscription_id
            simple_user.save()

            self._send_email(
                subject="You have PLUS plan",
                message=(
                    "You have bought/renewed the plus plan. "
                    "Your access keys now have access to plus features."
                ),
                recipient_list=[simple_user.email],
            )

    def _handle_payment_failed(self, event):
        invoice = event["data"]["object"]
        email = invoice.get("customer_email")

        if email:
            try:
                simple_user = SimpleUser.objects.get(email=email)
                simple_user.plan = PlanEnum.FREE.value
                simple_user.save()

                self._send_email(
                    subject="PLUS plan renewal failed",
                    message=(
                        "Renewal payment failed, you are now on the free plan. "
                        "Renew your payment here: <link>"
                    ),
                    recipient_list=[simple_user.email],
                )
            except SimpleUser.DoesNotExist:
                logger.error(f"User with email {email} does not exist")

    def _send_email(self, subject, message, recipient_list):
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, recipient_list)


stripe_webhook_view = StripeWebhookView.as_view()
