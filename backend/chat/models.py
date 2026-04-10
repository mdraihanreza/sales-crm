from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    name = models.CharField(max_length=255, blank=True)
    is_group = models.BooleanField(default=False)
    is_dummy = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_chat_rooms"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or f"Room {self.pk}"


class ChatParticipant(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_participations")
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="participants")
    is_dummy = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "room")
        ordering = ["joined_at"]


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    is_dummy = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]


class Mention(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mentions")
    mentioned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mentions"
    )
    is_dummy = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        unique_together = ("message", "mentioned_user")
