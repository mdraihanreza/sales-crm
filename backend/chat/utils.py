import re

from django.db.models import Count, Max
from django.utils import timezone
from django.utils.text import slugify

from .models import ChatParticipant, ChatRoom, Mention, Message


MENTION_PATTERN = re.compile(r"@([\w-]+)")


def get_user_chat_handle(user):
    base = slugify(user.name) or user.email.split("@")[0]
    return f"{base}-{user.id}"


def get_room_display_name(room, current_user):
    if room.is_group and room.name:
        return room.name

    other_participants = [participant.user.name for participant in room.participants.all() if participant.user_id != current_user.id]
    if other_participants:
        return ", ".join(other_participants)
    return room.name or "Direct chat"


def mark_room_as_read(room, user):
    now = timezone.now()
    ChatParticipant.objects.filter(room=room, user=user).update(last_read_at=now)
    Message.objects.filter(room=room).exclude(sender=user).update(is_read=True)


def resolve_mentions_for_sender(room, sender):
    Mention.objects.filter(
        mentioned_user=sender,
        is_resolved=False,
        message__room=room,
    ).exclude(message__sender=sender).update(is_resolved=True)


def extract_mentions(message):
    return set(MENTION_PATTERN.findall(message))


def create_mentions_for_message(message):
    room_participants = ChatParticipant.objects.select_related("user").filter(room=message.room)
    user_by_handle = {get_user_chat_handle(participant.user): participant.user for participant in room_participants}
    mentions = []
    for handle in extract_mentions(message.content):
        mentioned_user = user_by_handle.get(handle)
        if mentioned_user and mentioned_user.id != message.sender_id:
            mention, _ = Mention.objects.get_or_create(
                message=message,
                mentioned_user=mentioned_user,
                defaults={"is_dummy": message.is_dummy},
            )
            if mention.is_dummy != message.is_dummy:
                mention.is_dummy = message.is_dummy
                mention.save(update_fields=["is_dummy"])
            mentions.append(mention)
    return mentions


def find_or_create_direct_room(current_user, other_user):
    existing_room = (
        ChatRoom.objects.filter(is_group=False, participants__user=current_user)
        .filter(participants__user=other_user)
        .annotate(participant_count=Count("participants"))
        .filter(participant_count=2)
        .distinct()
        .first()
    )
    if existing_room:
        return existing_room, False

    room = ChatRoom.objects.create(created_by=current_user, is_group=False, name="")
    ChatParticipant.objects.bulk_create(
        [
            ChatParticipant(room=room, user=current_user),
            ChatParticipant(room=room, user=other_user),
        ]
    )
    return room, True


def create_group_room(*, current_user, name, users):
    room = ChatRoom.objects.create(created_by=current_user, is_group=True, name=name)
    participants = [ChatParticipant(room=room, user=current_user)]
    for user in users:
        if user.id != current_user.id:
            participants.append(ChatParticipant(room=room, user=user))
    ChatParticipant.objects.bulk_create(participants)
    return room


def room_queryset_for_user(user):
    return (
        ChatRoom.objects.filter(participants__user=user)
        .prefetch_related("participants__user")
        .annotate(message_count=Count("messages"), last_activity=Max("messages__timestamp"))
        .order_by("-last_activity", "-created_at")
        .distinct()
    )
