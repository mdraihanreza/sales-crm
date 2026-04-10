from django.contrib import admin

from .models import Bid, BidPlatform, BidProfile


@admin.register(BidPlatform)
class BidPlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "is_active", "sort_order", "created_at")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "value")
    prepopulated_fields = {"value": ("name",)}
    list_per_page = 25


@admin.register(BidProfile)
class BidProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "is_active", "sort_order", "created_at")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "value")
    prepopulated_fields = {"value": ("name",)}
    list_per_page = 25


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("id", "user", "platform", "profile", "connects", "status", "is_dummy", "created_at")
    list_filter = ("platform", "status", "profile", "is_dummy", "created_at")
    list_per_page = 25
    search_fields = ("user__email", "job_link", "profile")
