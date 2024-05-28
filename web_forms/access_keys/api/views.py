from django.core.mail import send_mail
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from web_forms.access_keys.models import AccessKey

from .serializers import AccessKeySerializer


class AccessKeyViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = AccessKeySerializer
    queryset = AccessKey.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()

        subject = "Your SimpleForms.io Access Key!"
        message = f"Here is your access key: {instance.id}"
        recipient_list = [instance.email]
        # TODO move to variable
        send_mail(
            subject,
            message,
            "simpleforms@bitgeese.io",
            recipient_list,
            fail_silently=False,
        )
