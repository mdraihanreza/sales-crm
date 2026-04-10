from rest_framework import serializers

from users.models import User

from .models import ChatParticipant, ChatRoom, Mention, Message
from .utils import get_room_display_name, get_user_chat_handle


class ChatUserSerializer(serializers.ModelSerializer):
    chat_handle = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name", "email", "role", "chat_handle")

    def get_chat_handle(self, obj):
        return get_user_chat_handle(obj)


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    has_unresolved_mentions = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "name",
            "display_name",
            "is_group",
            "created_at",
            "participants",
            "unread_count",
            "last_message_preview",
            "has_unresolved_mentions",
        )

    def get_participants(self, obj):
        participants = [participant.user for participant in obj.participants.all()]
        return ChatUserSerializer(participants, many=True).data

    def get_display_name(self, obj):
        return get_room_display_name(obj, self.context["request"].user)

    def get_last_message_preview(self, obj):
        last_message = obj.messages.order_by("-timestamp").select_related("sender").first()
        if not last_message:
            return None
        return {
            "content": last_message.content[:120],
            "sender_name": last_message.sender.name,
            "timestamp": last_message.timestamp,
        }

    def get_has_unresolved_mentions(self, obj):
        user = self.context["request"].user
        return Mention.objects.filter(message__room=obj, mentioned_user=user, is_resolved=False).exists()

    def get_unread_count(self, obj):
        user = self.context["request"].user
        participant = obj.participants.filter(user=user).first()
        unread_messages = obj.messages.exclude(sender=user)
        if participant and participant.last_read_at:
            unread_messages = unread_messages.filter(timestamp__gt=participant.last_read_at)
        return unread_messages.count()


class CreateRoomSerializer(serializers.Serializer):
    is_group = serializers.BooleanField(default=False)
    name = serializers.CharField(required=False, allow_blank=False)
    participant_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)

    def validate(self, attrs):
        participant_ids = list(dict.fromkeys(attrs["participant_ids"]))
        users = list(User.objects.filter(id__in=participant_ids))
        if len(users) != len(participant_ids):
            raise serializers.ValidationError("One or more selected users do not exist.")

        if attrs["is_group"]:
            if not attrs.get("name"):
                raise serializers.ValidationError("Group chats require a name.")
            if len(users) < 2:
                raise serializers.ValidationError("Group chats require at least two selected users.")
        else:
            if len(users) != 1:
                raise serializers.ValidationError("Direct chat creation requires exactly one target user.")

        attrs["users"] = users
        return attrs


class MessageSerializer(serializers.ModelSerializer):
    sender = ChatUserSerializer(read_only=True)
    mention_handles = serializers.SerializerMethodField()
    highlight_for_current_user = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "room",
            "sender",
            "content",
            "timestamp",
            "is_read",
            "mention_handles",
            "highlight_for_current_user",
        )
        read_only_fields = ("id", "room", "sender", "timestamp", "is_read", "mention_handles", "highlight_for_current_user")

    def get_mention_handles(self, obj):
        return [get_user_chat_handle(mention.mentioned_user) for mention in obj.mentions.select_related("mentioned_user").all()]

    def get_highlight_for_current_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.mentions.filter(mentioned_user=request.user, is_resolved=False).exists()


class RoomMessagesSerializer(serializers.Serializer):
    room = ChatRoomSerializer()
    messages = MessageSerializer(many=True)
