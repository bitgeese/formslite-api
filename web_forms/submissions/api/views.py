import logging

from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import web_forms.access_keys.tasks as tasks
from web_forms.authentication import CsrfExemptSessionAuthentication
from web_forms.submissions.utils.spam_detection import is_spam
from web_forms.throttles import SubmissionRateThrottle
from web_forms.utils.emails import send_submission_email

from ..models import Submission as SubmissionAnalytics
from .serializers import SubmissionSerializer

logger = logging.getLogger(__name__)


class SubmissionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = (CsrfExemptSessionAuthentication,)
    parser_classes = [FormParser, MultiPartParser]
    throttle_classes = [SubmissionRateThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def post(self, request, *args, **kwargs):
        logger.info("Received submission request.")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            logger.info("Submission data is valid.")
            self.handle_valid_submission(serializer)
            return HttpResponseRedirect(serializer.validated_data["redirect"])
        logger.warning("Invalid submission data: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer(self, data):
        return SubmissionSerializer(data=data)

    def handle_valid_submission(self, serializer):
        access_key = serializer.validated_data["access_key"]
        validated_data = serializer.validated_data
        user_id = access_key.user.id
        access_key_id = access_key.id
        data = validated_data["data"]

        logger.info(
            "Handling valid submission for access key %s by user %s",
            access_key_id,
            user_id,
        )

        # check for spam
        if is_spam(data, self.request):
            logger.info("Submission detected as spam for access key %s", access_key_id)
            SubmissionAnalytics.objects.create(access_key=access_key, is_spam=True)
        else:
            logger.info("Submission is not spam for access key %s", access_key_id)
            send_submission_email(access_key, validated_data)
            logger.info("Sent submission email for access key %s", access_key_id)
            SubmissionAnalytics.objects.create(access_key=access_key)
            logger.info(
                "Created SubmissionAnalytics entry for access key %s", access_key_id
            )
            if access_key.user.is_paid:
                logger.info(
                    "User is paid, scheduling additional tasks for access key %s",
                    access_key_id,
                )
                tasks.auto_respond_task.delay(user_id, validated_data)
                tasks.send_to_notion_task.delay(access_key_id, data)
                tasks.send_to_webhook_task.delay(access_key_id, data)
        access_key.use_access_key()
        logger.info("Access key usage incremented for access key %s", access_key_id)


submission_view = SubmissionView.as_view()
