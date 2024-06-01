# Generated by Django 5.0.6 on 2024-06-01 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("access_keys", "0004_simpleuser_remove_accesskey_email_accesskey_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="accesskey",
            name="plan",
        ),
        migrations.AddField(
            model_name="simpleuser",
            name="plan",
            field=models.CharField(
                choices=[("free", "Free"), ("plus", "Plus"), ("elite", "Elite")],
                default="free",
                max_length=10,
            ),
        ),
    ]
