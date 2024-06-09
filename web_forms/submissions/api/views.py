import logging

from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

import web_forms.access_keys.tasks as tasks
from web_forms.authentication import CsrfExemptSessionAuthentication
from web_forms.throttles import SubmissionRateThrottle
from web_forms.utils.emails import send_submission_email

from .serializers import SubmissionSerializer

logger = logging.getLogger(__name__)


class SubmissionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = (CsrfExemptSessionAuthentication,)
    parser_classes = [FormParser, MultiPartParser]
    throttle_classes = [SubmissionRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.handle_valid_submission(serializer)
            return HttpResponseRedirect(serializer.validated_data["redirect"])
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer(self, data):
        return SubmissionSerializer(data=data)

    def handle_valid_submission(self, serializer):
        access_key = serializer.validated_data["access_key"]
        validated_data = serializer.validated_data
        user_id = access_key.user.id
        access_key_id = access_key.id
        data = validated_data["data"]
        send_submission_email(access_key, validated_data)
        if access_key.user.is_paid:
            tasks.auto_respond_task.delay(user_id, validated_data)
            tasks.send_to_notion_task.delay(access_key_id, data)
            tasks.send_to_webhook_task.delay(access_key_id, data)
        access_key.use_access_key()


submission_view = SubmissionView.as_view()
