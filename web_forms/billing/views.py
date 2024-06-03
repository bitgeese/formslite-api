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
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Handle the event
        logger.info(event["type"])
        if event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            logger.info(invoice)
            # customer_id = invoice['customer']
            subscription_id = invoice["subscription"]
            email = invoice["customer_email"]
            # Match the email with the user and update the subscription plan to paid
            simple_user, _ = SimpleUser.objects.get_or_create(email=email)
            simple_user.plan = PlanEnum.PLUS.value
            simple_user.stripe_subscription_id = subscription_id
            simple_user.save()

            # send notification
            subject = "You have PLUS plan"
            message = (
                "You have bought/renewed the plus plan."
                "Your access keys now have access to plus features."
            )
            from_email = settings.DEFAULT_FROM_EMAIL
            send_mail(subject, message, from_email, [simple_user.email])

        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            # customer_id = invoice['customer']
            email = invoice["customer_email"]
            # Match the email with the user and update the subscription plan to free
            simple_user = SimpleUser.objects.get(email=email)
            if simple_user:
                simple_user.plan = PlanEnum.FREE.value
                simple_user.save()

                # send notification
                subject = "PLUS plan renewal failed"
                message = (
                    "Renewal payment failed, you are on freeplan"
                    "Renew payment here: <>"
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                send_mail(subject, message, from_email, [simple_user.email])

        return JsonResponse({"status": "success"}, status=200)


stripe_webhook_view = StripeWebhookView.as_view()
