import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DashboardConfig(AppConfig):
    name = "web_forms.dashboard"
    verbose_name = _("Dashboard")

    def ready(self):
        with contextlib.suppress(ImportError):
            import web_forms.dashboard.signals  # noqa: F401
