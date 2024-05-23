from django.contrib import admin

from .models import AccessKey


@admin.register(AccessKey)
class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email"]
    search_fields = ["email"]
