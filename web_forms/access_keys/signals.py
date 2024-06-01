from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import AccessKey, SimpleUser


@receiver(pre_save, sender=AccessKey)
def create_simple_user(sender, instance, **kwargs):
    if not SimpleUser.objects.filter(email=instance.user.email).exists():
        simple_user, created = SimpleUser.objects.get_or_create(
            email=instance.user.email
        )
        instance.user = simple_user


@receiver(post_save, sender=AccessKey)
def send_access_key_created_email_to_admin(sender, instance, created, **kwargs):
    if created:
        subject = "New AccessKey Created"
        message = (
            "A new AccessKey has been created.\n\nDetails:\nAccessKey "
            f"User: {instance.user.email}\nAccess Key: {instance.id}"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [admin[1] for admin in settings.ADMINS]
        send_mail(subject, message, from_email, recipient_list)
