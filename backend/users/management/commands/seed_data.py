import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bids.models import Bid
from chat.models import ChatParticipant, ChatRoom, Message
from chat.utils import create_mentions_for_message, get_user_chat_handle, resolve_mentions_for_sender
from users.demo_data import DEMO_USERS, cleanup_demo_data
from users.models import User


class Command(BaseCommand):
    help = "Seed demo users, bids, chats, mentions, and unread states for CRM testing."

    def handle(self, *args, **options):
        with transaction.atomic():
            cleanup_demo_data()

            admin_user = User.objects.filter(role=User.ROLE_ADMIN, is_dummy=False).order_by("id").first()
            if not admin_user:
                self.stderr.write(self.style.ERROR("No real admin user found. Aborting seed."))
                return

            demo_users = self._create_demo_users()
            self._seed_bids(demo_users)
            self._seed_chat(admin_user, demo_users)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _create_demo_users(self):
        users = []
        for email, name in DEMO_USERS:
            user = User.objects.create_user(
                email=email,
                password="1234",
                name=name,
                role=User.ROLE_TEAM,
                is_dummy=True,
            )
            users.append(user)
        return users

    def _seed_bids(self, users):
        now = timezone.now()
        profiles = ["Profile1", "Profile2", "Profile3", "Profile4"]
        platforms = [Bid.PLATFORM_UPWORK, Bid.PLATFORM_FREELANCER]
        performance_profiles = {
            "Rahim": [0.45, 0.25, 0.10, 0.20],
            "Karim": [0.30, 0.20, 0.08, 0.42],
            "John": [0.40, 0.22, 0.12, 0.26],
            "Maria": [0.22, 0.22, 0.18, 0.38],
            "Sophia": [0.34, 0.26, 0.10, 0.30],
            "Liam": [0.28, 0.18, 0.14, 0.40],
            "Noah": [0.42, 0.21, 0.08, 0.29],
            "Emma": [0.26, 0.24, 0.17, 0.33],
        }
        statuses = [Bid.STATUS_REPLY, Bid.STATUS_CALL, Bid.STATUS_CLOSED, Bid.STATUS_PENDING]

        for user in users:
            bid_count = random.randint(60, 160)
            bids = []
            bid_timestamps = []
            status_weights = performance_profiles[user.name]
            for index in range(bid_count):
                day_offset = random.randint(0, 89)
                minute_offset = random.randint(0, 8 * 60)
                created_at = now - timedelta(days=day_offset, hours=random.randint(1, 10), minutes=minute_offset)
                bid_timestamps.append(created_at)
                platform = random.choices(platforms, weights=[0.75, 0.25])[0]
                status = random.choices(statuses, weights=status_weights)[0]
                bids.append(
                    Bid(
                        user=user,
                        platform=platform,
                        profile=random.choice(profiles),
                        job_link=f"https://{platform}.example/jobs/{user.id}-{index}-{random.randint(1000, 9999)}",
                        connects=random.randint(5, 20),
                        status=status,
                        is_dummy=True,
                    )
                )
            created_bids = Bid.objects.bulk_create(bids)
            for bid, created_at in zip(created_bids, bid_timestamps):
                Bid.objects.filter(pk=bid.pk).update(created_at=created_at)

    def _seed_chat(self, admin_user, demo_users):
        now = timezone.now()
        rooms = []
        all_users = [admin_user, *demo_users]

        for user in demo_users[:5]:
            room_created_at = now - timedelta(days=random.randint(10, 40))
            room = ChatRoom.objects.create(
                name="",
                is_group=False,
                created_by=admin_user,
                is_dummy=True,
            )
            ChatRoom.objects.filter(pk=room.pk).update(created_at=room_created_at)
            ChatParticipant.objects.bulk_create(
                [
                    ChatParticipant(room=room, user=admin_user, is_dummy=True),
                    ChatParticipant(room=room, user=user, is_dummy=True),
                ]
            )
            rooms.append(room)

        direct_pairs = [
            (demo_users[0], demo_users[2]),
            (demo_users[3], demo_users[5]),
        ]
        for first_user, second_user in direct_pairs:
            room_created_at = now - timedelta(days=random.randint(8, 28))
            room = ChatRoom.objects.create(
                name="",
                is_group=False,
                created_by=admin_user,
                is_dummy=True,
            )
            ChatRoom.objects.filter(pk=room.pk).update(created_at=room_created_at)
            ChatParticipant.objects.bulk_create(
                [
                    ChatParticipant(room=room, user=first_user, is_dummy=True),
                    ChatParticipant(room=room, user=second_user, is_dummy=True),
                ]
            )
            rooms.append(room)

        group_specs = [
            ("Sales Team", [admin_user, demo_users[0], demo_users[1], demo_users[3]]),
            ("Developers", [admin_user, demo_users[2], demo_users[4], demo_users[5]]),
            ("Growth Ops", [admin_user, demo_users[6], demo_users[7], demo_users[1]]),
        ]

        for name, participants in group_specs:
            room_created_at = now - timedelta(days=random.randint(5, 30))
            room = ChatRoom.objects.create(
                name=name,
                is_group=True,
                created_by=admin_user,
                is_dummy=True,
            )
            ChatRoom.objects.filter(pk=room.pk).update(created_at=room_created_at)
            ChatParticipant.objects.bulk_create(
                [ChatParticipant(room=room, user=participant, is_dummy=True) for participant in participants]
            )
            rooms.append(room)

        message_templates = [
            "Morning team, checking the bid pipeline for today.",
            "We received a strong reply on the latest proposal.",
            "Please review the connects burn rate before noon.",
            "Client asked for a follow-up call tomorrow.",
            "Let us close the loop on yesterday's shortlist.",
            "Sharing quick update before the dashboard review.",
            "Need eyes on the new lead qualification notes.",
            "Pushing a status update for this account.",
        ]

        for room in rooms:
            participants = list(room.participants.select_related("user"))
            room_users = [participant.user for participant in participants]
            total_messages = random.randint(24, 72)
            message_times = sorted(
                [
                    now - timedelta(
                        days=random.randint(2, 45),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )
                    for _ in range(total_messages)
                ]
            )
            unresolved_targets = set(random.sample([user.id for user in room_users if user.id != admin_user.id], k=max(1, min(2, len(room_users) - 1))))

            for index in range(total_messages):
                sender = random.choice(room_users)
                resolve_mentions_for_sender(room, sender)

                content = random.choice(message_templates)
                if len(room_users) > 1 and random.random() < 0.24:
                    mention_target = random.choice([user for user in room_users if user.id != sender.id])
                    content = f"{content} @{get_user_chat_handle(mention_target)}"
                    if index >= total_messages - 3:
                        unresolved_targets.add(mention_target.id)

                message_time = message_times[index]
                message = Message.objects.create(
                    sender=sender,
                    room=room,
                    content=content,
                    is_read=index < total_messages - random.randint(2, 6),
                    is_dummy=True,
                )
                Message.objects.filter(pk=message.pk).update(timestamp=message_time)
                message.timestamp = message_time
                create_mentions_for_message(message)

            room_messages = list(room.messages.order_by("timestamp"))
            for participant in participants:
                candidate_messages = [message for message in room_messages if message.sender_id != participant.user_id]
                if not candidate_messages:
                    continue

                if participant.user_id in unresolved_targets:
                    participant.last_read_at = candidate_messages[max(0, len(candidate_messages) - random.randint(4, 8))].timestamp
                else:
                    participant.last_read_at = candidate_messages[max(0, len(candidate_messages) - random.randint(1, 3))].timestamp
                participant.save(update_fields=["last_read_at"])

            latest_messages = room.messages.order_by("-timestamp")[:5]
            Message.objects.filter(id__in=[message.id for message in latest_messages]).update(is_read=False)

            unresolved_mentions = room.messages.filter(mentions__is_resolved=False).distinct()
            if not unresolved_mentions.exists() and len(room_users) > 1:
                sender = admin_user
                target = next(user for user in room_users if user.id != sender.id)
                final_message_time = now - timedelta(minutes=random.randint(5, 120))
                final_message = Message.objects.create(
                    sender=sender,
                    room=room,
                    content=f"Need your reply on this thread @{get_user_chat_handle(target)}",
                    is_read=False,
                    is_dummy=True,
                )
                Message.objects.filter(pk=final_message.pk).update(timestamp=final_message_time)
                create_mentions_for_message(final_message)
