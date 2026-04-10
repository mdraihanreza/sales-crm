from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User

from .models import ChatRoom, Message
from .permissions import IsChatParticipant
from .serializers import (
    ChatRoomSerializer,
    ChatUserSerializer,
    CreateRoomSerializer,
    MessageSerializer,
    RoomMessagesSerializer,
)
from .utils import create_group_room, find_or_create_direct_room, mark_room_as_read, room_queryset_for_user


class ChatUserDirectoryView(generics.ListAPIView):
    serializer_class = ChatUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return room_queryset_for_user(self.request.user)


class CreateRoomView(generics.GenericAPIView):
    serializer_class = CreateRoomSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["is_group"]:
            room = create_group_room(
                current_user=request.user,
                name=serializer.validated_data["name"],
                users=serializer.validated_data["users"],
            )
            created = True
        else:
            room, created = find_or_create_direct_room(request.user, serializer.validated_data["users"][0])

        room.refresh_from_db()
        room = ChatRoom.objects.prefetch_related("participants__user").get(pk=room.pk)
        return Response(
            {"created": created, "room": ChatRoomSerializer(room, context={"request": request}).data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RoomMessagesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsChatParticipant]
    serializer_class = RoomMessagesSerializer

    def get(self, request, room_id):
        room = ChatRoom.objects.prefetch_related("participants__user").get(
            pk=room_id, participants__user=request.user
        )
        mark_room_as_read(room, request.user)
        messages = Message.objects.filter(room=room).select_related("sender").prefetch_related("mentions__mentioned_user")
        payload = {
            "room": ChatRoomSerializer(
                ChatRoom.objects.prefetch_related("participants__user").get(pk=room.pk),
                context={"request": request},
            ).data,
            "messages": MessageSerializer(messages, many=True, context={"request": request}).data,
        }
        return Response(payload)
