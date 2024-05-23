import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccessKeyConfig(AppConfig):
    name = "web_forms.access_keys"
    verbose_name = _("Access Keys")

    def ready(self):
        with contextlib.suppress(ImportError):
            import web_forms.access_keys.signals  # noqa: F401
