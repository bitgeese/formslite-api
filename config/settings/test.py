"""
With these settings, tests run faster.
"""

from .base import *  # noqa: F401, F403
from .base import TEMPLATES, env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="JRqCycik7zJCfzXjEuPm6t4D9jDekSgwxDnTFC31cKSJq6egWdcfIKt4n0cLZ0OM",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore[index]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "http://media.testserver"
# Your stuff...
# ------------------------------------------------------------------------------

STRIPE_SECRET_KEY = (
    "sk_test_51PMJytP7ONwv6j65viEmHUk1gw8VmfwjPOjj2hiCcUH9neaj1GYJbRWmTI"
    "vtOaJokJb4kNhmy6FK3YfqwxkyEvxk00qPGSaVm5"
)
STRIPE_WEBHOOK_SECRET = "whsec_ttXWsX4B1qdcKbdtKTYb1686y1ptG4qQ"
