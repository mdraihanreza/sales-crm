from django.conf import settings
from django.db import models


class LeadStatus(models.Model):
    client_name = models.CharField(max_length=255)
    current_status = models.TextField()
    chat_room_link = models.URLField(blank=True)
    profile = models.CharField(max_length=100, blank=True)
    is_archived = models.BooleanField(default=False)
    is_dummy = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_lead_statuses",
    )
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="checked_lead_statuses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["is_archived", "-updated_at"]
        verbose_name = "Lead status"
        verbose_name_plural = "Lead statuses"

    def __str__(self):
        return f"{self.client_name} - {self.profile or 'No profile'}"
