import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatParticipant, ChatRoom, Message
from .serializers import MessageSerializer
from .utils import create_mentions_for_message, resolve_mentions_for_sender


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_room_{self.room_id}"

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        is_participant = await self._is_participant()
        if not is_participant:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        content = (payload.get("content") or "").strip()
        if not content:
            await self.send(text_data=json.dumps({"type": "error", "message": "Message content cannot be empty."}))
            return

        message_payload, participant_ids = await self._create_message(content)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message_payload,
            },
        )

        for participant_id in participant_ids:
            if participant_id != self.user.id:
                await self.channel_layer.group_send(
                    f"user_{participant_id}",
                    {
                        "type": "chat.notification",
                        "notification": {
                            "kind": "new_message",
                            "room_id": self.room_id,
                            "message": message_payload,
                            "is_mention": participant_id in message_payload["mentioned_user_ids"],
                        },
                    },
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"type": "message", "message": event["message"]}, default=str))

    @database_sync_to_async
    def _is_participant(self):
        return ChatParticipant.objects.filter(room_id=self.room_id, user=self.user).exists()

    @database_sync_to_async
    def _create_message(self, content):
        room = ChatRoom.objects.get(pk=self.room_id)
        resolve_mentions_for_sender(room, self.user)
        message = Message.objects.create(room=room, sender=self.user, content=content)
        mentions = create_mentions_for_message(message)
        participant_ids = list(room.participants.values_list("user_id", flat=True))
        serialized = MessageSerializer(message, context={"request": None}).data
        serialized["mentioned_user_ids"] = [mention.mentioned_user_id for mention in mentions]
        serialized["room_id"] = room.id
        return serialized, participant_ids


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        self.notification_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.notification_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.notification_group_name, self.channel_name)

    async def chat_notification(self, event):
        await self.send(text_data=json.dumps({"type": "notification", "notification": event["notification"]}, default=str))
