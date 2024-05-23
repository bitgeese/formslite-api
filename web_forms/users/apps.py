import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "web_forms.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import web_forms.users.signals  # noqa: F401
