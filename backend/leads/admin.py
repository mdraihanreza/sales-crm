from django.contrib import admin

from .models import LeadStatus


@admin.register(LeadStatus)
class LeadStatusAdmin(admin.ModelAdmin):
    date_hierarchy = "updated_at"
    list_display = ("client_name", "profile", "last_updated_by", "is_archived", "is_dummy", "updated_at")
    list_filter = ("is_archived", "is_dummy", "profile", "updated_at")
    search_fields = ("client_name", "current_status", "chat_room_link", "last_updated_by__name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
