from django.db import models

from web_forms.access_keys.models import AccessKey


class Submission(models.Model):
    access_key = models.ForeignKey(
        AccessKey, on_delete=models.CASCADE, related_name="submissions"
    )
    data = models.JSONField()
