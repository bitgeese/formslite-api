from django.db import models

from web_forms.access_keys.models import AccessKey
from web_forms.models import BaseModel

class Submission(BaseModel):
    access_key = models.ForeignKey(
        AccessKey, on_delete=models.CASCADE, related_name="submissions"
    )
    data = models.JSONField()
