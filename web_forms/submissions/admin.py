from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class Submission(admin.ModelAdmin):
    list_display = ["id", "access_key", "data"]
    search_fields = ["access_key"]
