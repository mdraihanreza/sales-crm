from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "role", "is_staff", "is_active", "is_dummy", "created_at")
    list_filter = ("role", "is_staff", "is_active", "is_dummy", "created_at")
    list_per_page = 25
    search_fields = ("email", "name")
    readonly_fields = ("last_login", "created_at", "updated_at")

    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Profile", {"fields": ("name", "role", "is_dummy")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "role", "is_dummy", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
