import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubmissionConfig(AppConfig):
    name = "web_forms.submissions"
    verbose_name = _("Submissions")

    def ready(self):
        with contextlib.suppress(ImportError):
            import web_forms.submissions.signals  # noqa: F401
