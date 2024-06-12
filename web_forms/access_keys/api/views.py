import logging

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from web_forms.authentication import CsrfExemptSessionAuthentication
from web_forms.throttles import AccessKeyCreateRateThrottle

from .serializers import AccessKeySerializer

logger = logging.getLogger(__name__)


class AccessKeyCreateAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = (CsrfExemptSessionAuthentication,)
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    throttle_classes = [AccessKeyCreateRateThrottle]

    def post(self, request, *args, **kwargs):
        logger.info("Received request to create access key.")
        serializer = AccessKeySerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            logger.info(
                "Access key created successfully for email: %s", instance.user.email
            )

            subject = "Your FormsLite.io Access Key!"
            message = f"Here is your access key: {instance.id}"
            recipient_list = [instance.user.email]
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            logger.info("Email sent successfully to: %s", recipient_list)
            return HttpResponseRedirect("https://formslite.io")
        logger.warning("Invalid data received: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


access_key_create_api = AccessKeyCreateAPIView.as_view()
