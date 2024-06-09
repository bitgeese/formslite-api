from celery import shared_task

from web_forms.utils.emails import send_submission_email

from .models import AccessKey, SimpleUser


@shared_task
def reset_access_key_usage():
    access_keys = AccessKey.objects.filter(is_active=True)
    for access_key in access_keys:
        access_key.reset_usage()


@shared_task
def send_submission_email_task(access_key_id, validated_data):
    access_key = AccessKey.objects.get(id=access_key_id)
    send_submission_email(access_key, validated_data)


@shared_task
def auto_respond_task(user_id, validated_data):
    user = SimpleUser.objects.get(id=user_id)
    user.auto_respond(validated_data)


@shared_task
def send_to_notion_task(access_key_id, data):
    access_key = AccessKey.objects.get(id=access_key_id)
    access_key.send_to_notion(data)


@shared_task
def send_to_webhook_task(access_key_id, data):
    access_key = AccessKey.objects.get(id=access_key_id)
    access_key.send_to_webhook(data)
