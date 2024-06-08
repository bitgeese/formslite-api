from django.contrib.auth.models import BaseUserManager


class SimpleUserManager(BaseUserManager):
    def create_user(
        self,
        email,
        plan="free",
        stripe_subscription_id="",
        auto_reply=False,
        **extra_fields
    ):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            plan=plan,
            stripe_subscription_id=stripe_subscription_id,
            auto_reply=auto_reply,
            **extra_fields
        )
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        password=None,
        plan="free",
        stripe_subscription_id="",
        auto_reply=False,
        **extra_fields
    ):
        user = self.create_user(
            email, plan, stripe_subscription_id, auto_reply, **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        if password:
            user.set_password(password)  # Set password for superusers
        user.save(using=self._db)
        return user
