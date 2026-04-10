from rest_framework.permissions import BasePermission

from .models import ChatParticipant


class IsChatParticipant(BasePermission):
    def has_permission(self, request, view):
        room_id = view.kwargs.get("room_id") or request.data.get("room_id")
        if not room_id or not request.user.is_authenticated:
            return False
        return ChatParticipant.objects.filter(room_id=room_id, user=request.user).exists()
