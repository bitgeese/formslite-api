# Generated by Django 5.0.6 on 2024-06-08 05:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("access_keys", "0015_alter_notionlink_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notionlink",
            name="access_key",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notion_links",
                to="access_keys.accesskey",
            ),
        ),
    ]
