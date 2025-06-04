from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "username", "email", "created_at")
    search_fields = ("id", "username", "first_name", "last_name", "email")
    list_filter = ("created_at",)
    ordering = ("created_at",)
    readonly_fields = ("id", "created_at")
    fieldsets = (
        (
            "Main information",
            {
                "fields": (
                    "id",
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "created_at",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": ("id", "first_name", "last_name", "username"),
            },
        ),
    )
