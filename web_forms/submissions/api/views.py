from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from web_forms.authentication import CsrfExemptSessionAuthentication
from web_forms.submissions.models import Submission
from web_forms.utils import format_dict_for_email

from .serializers import SubmissionSerializer


class SubmissionViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = SubmissionSerializer
    queryset = Submission.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = CsrfExemptSessionAuthentication
    parser_classes = [FormParser, MultiPartParser]
    lookup_field = "access_key__id"

    def perform_create(self, serializer):
        instance = serializer.save()

        subject = "New Submission Received"
        text_content = (
            "A new submission has been received. "
            "Here are the details:\n\nAccess Key: {}\n\n{}".format(
                instance.access_key.id, format_dict_for_email(instance.data)
            )
        )
        html_content = format_html(
            "<p>A new submission has been received.</p>"
            "<p>Here are the details:</p>"
            "<p>Access Key: {}</p>"
            "<div>{}</div>".format(
                instance.access_key.id, format_dict_for_email(instance.data)
            )
        )

        recipient_list = [instance.access_key.email]

        msg = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, recipient_list
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return HttpResponseRedirect("https://www.formslite.io/success")

    @action(detail=False, methods=["get"], url_path="(?P<access_key_id>[^/.]+)")
    def get_submissions_by_access_key(self, request, access_key_id):
        submissions = self.queryset.filter(access_key_id=access_key_id)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
