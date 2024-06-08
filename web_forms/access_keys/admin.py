from django.contrib import admin

from .models import AccessKey, SimpleUser, UserSettings


@admin.register(AccessKey)
class AccessKeyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "user"]
    search_fields = ["user"]


@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ["email", "plan"]
    search_fields = ["email"]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "auto_responder_enabled"]
    search_fields = ["user"]
