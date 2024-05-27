# ruff: noqa: E501
from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

# GENERAL
SECRET_KEY = env("DJANGO_SECRET_KEY")

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*",
                 "healthcheck.railway.app",
                 "web-forms-frontend-git-main-maciej-janowskis-projects.vercel.app"
                 ]  # noqa: S104
#ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# EMAIL
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["anymail"]
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="SimpleForms.io <simpleforms@bitgeese.io>",
)
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[SimpleForms.io] ",
)
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),
    "SENDGRID_API_URL": env("SENDGRID_API_URL", default="https://api.sendgrid.com/v3/"),
}


# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions"]
# Celery
# ------------------------------------------------------------------------------

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# Your stuff...
# ------------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
    "https://web-forms-frontend-git-main-maciej-janowskis-projects.vercel.app"
    # NOTE: Place your custom url here if any
]

CORS_ALLOWED_ORIGINS = [
    "https://*.up.railway.app",
    "https://web-forms-frontend-git-main-maciej-janowskis-projects.vercel.app"
]