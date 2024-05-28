import logging

from django.conf import settings
from django.core.mail import send_mail
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from web_forms.access_keys.models import AccessKey
from web_forms.authentication import CsrfExemptSessionAuthentication

from .serializers import AccessKeySerializer

logger = logging.getLogger(__name__)


class AccessKeyViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = AccessKeySerializer
    queryset = AccessKey.objects.all()
    # authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()

        subject = "Your FormsLite.io Access Key!"
        message = f"Here is your access key: {instance.id}"
        recipient_list = [instance.email]
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            logger.info(f"Email sent successfully to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {instance.email}: {e}")
