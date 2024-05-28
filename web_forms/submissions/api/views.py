from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from web_forms.authentication import CsrfExemptSessionAuthentication
from web_forms.utils import format_dict_for_email

from .serializers import SubmissionSerializer


class SubmissionView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = (CsrfExemptSessionAuthentication,)
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            access_key = serializer.validated_data["access_key"]
            data = serializer.validated_data["data"]

            subject = "New Submission Received"
            text_content = (
                "A new submission has been received. "
                "Here are the details:\n\nAccess Key: {}\n\n{}".format(
                    access_key.id, format_dict_for_email(data)
                )
            )
            html_content = format_html(
                "<p>A new submission has been received.</p>"
                "<p>Here are the details:</p>"
                "<p>Access Key: {}</p>"
                "<div>{}</div>".format(access_key.id, format_dict_for_email(data))
            )

            recipient_list = [access_key.email]

            msg = EmailMultiAlternatives(
                subject, text_content, settings.DEFAULT_FROM_EMAIL, recipient_list
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            return Response(
                {"message": "Email sent successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


submission_view = SubmissionView.as_view()
