from django.contrib import admin

from .models import ChatParticipant, ChatRoom, Mention, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_group", "created_by", "is_dummy", "created_at")
    list_filter = ("is_group", "is_dummy", "created_at")
    search_fields = ("name", "created_by__email", "created_by__name")
    list_per_page = 25


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user", "is_dummy", "joined_at", "last_read_at")
    list_filter = ("is_dummy", "joined_at")
    search_fields = ("room__name", "user__email", "user__name")
    list_per_page = 25


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    date_hierarchy = "timestamp"
    list_display = ("id", "room", "sender", "short_content", "is_read", "is_dummy", "timestamp")
    list_filter = ("is_read", "is_dummy", "timestamp")
    search_fields = ("content", "sender__email", "sender__name", "room__name")
    list_per_page = 25

    @admin.display(description="Content")
    def short_content(self, obj):
        return f"{obj.content[:80]}..." if len(obj.content) > 80 else obj.content


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "mentioned_user", "is_resolved", "is_dummy")
    list_filter = ("is_resolved", "is_dummy")
    search_fields = ("mentioned_user__email", "mentioned_user__name", "message__content")
    list_per_page = 25
