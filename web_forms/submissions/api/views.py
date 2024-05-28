from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from web_forms.submissions.models import Submission

from .serializers import SubmissionSerializer


class SubmissionViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser]
    lookup_field = "access_key__id"

    def perform_create(self, serializer):
        instance = serializer.save()

        subject = "New Submission Received"
        message = "A new submission has been received. Here are the details:\n\nAccess Key: {}\nData: {}".format(
            instance.access_key.id, instance.data
        )
        recipient_list = [instance.access_key.email]
        send_mail(
            subject,
            message,
            "simpleforms@bitgeese.io",
            recipient_list,
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return HttpResponseRedirect("https://web-forms-frontend.vercel.app/success")

    @action(detail=False, methods=["get"], url_path="(?P<access_key_id>[^/.]+)")
    def get_submissions_by_access_key(self, request, access_key_id=None):
        if not access_key_id:
            return Response({"error": "Access key is required"}, status=400)
        submissions = self.queryset.filter(access_key_id=access_key_id)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
