from django.contrib import admin

from .models import AccessKey, SimpleUser


@admin.register(AccessKey)
class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "user"]
    search_fields = ["user"]


@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ["email"]
    search_fields = ["email"]
