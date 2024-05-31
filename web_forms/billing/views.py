import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Ensure the key is kept out of any version control system you might be using.
stripe.api_key = "sk_test_51PMJytP7ONwv6j65viEmHUk1gw8VmfwjPOjj2hiCcUH9neaj1GYJbRWmTIvtOaJokJb4kNhmy6FK3YfqwxkyEvxk00qPGSaVm5"

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_f11531a403b940596f63eb39587058ada01f9be159968d00d26e83115895dbc4'

class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
        else:
            print('Unhandled event type {}'.format(event['type']))

        return Response({'success': True}, status=status.HTTP_200_OK)


stripe_webhook_view = StripeWebhookView.as_view()