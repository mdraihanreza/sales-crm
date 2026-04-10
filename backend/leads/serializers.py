from rest_framework import serializers

from bids.models import BidProfile

from .models import LeadStatus


class LeadStatusSerializer(serializers.ModelSerializer):
    lead_check = serializers.CharField(source="last_updated_by.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.name", read_only=True)

    class Meta:
        model = LeadStatus
        fields = (
            "id",
            "last_updated",
            "client_name",
            "current_status",
            "lead_check",
            "chat_room_link",
            "profile",
            "is_archived",
            "is_dummy",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "lead_check", "created_by_name", "created_at", "updated_at", "last_updated", "is_dummy")

    last_updated = serializers.DateTimeField(source="updated_at", read_only=True)

    def validate_profile(self, value):
        if value and not BidProfile.objects.filter(value=value, is_active=True).exists():
            raise serializers.ValidationError("Select a valid active profile.")
        return value
