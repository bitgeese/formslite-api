import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BillingConfig(AppConfig):
    name = "web_forms.billing"
    verbose_name = _("Billing")

    def ready(self):
        with contextlib.suppress(ImportError):
            import web_forms.billing.signals  # noqa: F401
