from celery import shared_task

from .models import AccessKey


@shared_task
def reset_access_key_usage():
    access_keys = AccessKey.objects.filter(is_active=True)
    for access_key in access_keys:
        access_key.reset_usage()
