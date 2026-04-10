import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from bids.models import BidProfile
from leads.models import LeadStatus
from users.models import User


class Command(BaseCommand):
    help = "Seed dummy Lead Status Report rows for testing the shared lead tracker."

    def handle(self, *args, **options):
        with transaction.atomic():
            LeadStatus.objects.filter(is_dummy=True).delete()

            team_users = list(User.objects.filter(role=User.ROLE_TEAM, is_active=True).order_by("id"))
            fallback_user = User.objects.filter(role=User.ROLE_ADMIN, is_active=True).order_by("id").first()
            profiles = list(BidProfile.objects.filter(is_active=True).order_by("sort_order", "name").values_list("value", flat=True))

            if not team_users and not fallback_user:
                self.stderr.write(self.style.ERROR("No active users available for lead demo data."))
                return

            if not profiles:
                self.stderr.write(self.style.ERROR("No active bid profiles found. Add profiles before seeding leads."))
                return

            users = team_users or [fallback_user]
            created_count = self._seed_leads(users, profiles)

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} dummy lead status rows."))

    def _seed_leads(self, users, profiles):
        now = timezone.now()
        clients = [
            "Northstar Labs",
            "BluePeak Analytics",
            "Orbit Retail",
            "Nimbus Health",
            "Cedar Finance",
            "BrightPath Studio",
            "Atlas Logistics",
            "PrimeWave Media",
            "SignalWorks",
            "Riverstone Apps",
            "NovaHire",
            "UrbanNest",
            "CloudMint",
            "Vertex Legal",
            "LaunchGrid",
            "MarketMuse",
            "Silverline AI",
            "GreenByte",
            "Horizon Tutors",
            "PulseCommerce",
        ]
        status_templates = [
            "Discovery call completed. Waiting on scope confirmation and budget approval.",
            "Proposal sent. Client asked for examples related to CRM automation.",
            "Need follow-up today. Decision maker requested pricing clarification.",
            "Qualified lead. Technical requirements look aligned with our delivery capacity.",
            "Client shared reference product. Preparing revised timeline and milestone plan.",
            "Warm lead from marketplace. Waiting for reply after second follow-up.",
            "Call booked. Need to confirm stakeholder availability and meeting agenda.",
            "Negotiation stage. Client is comparing our offer with another vendor.",
            "Paused by client. Revisit next week with a smaller starting package.",
            "High-intent lead. Send final case study and ask for close confirmation.",
        ]

        for index, client in enumerate(clients):
            owner = random.choice(users)
            updated_at = now - timedelta(days=random.randint(0, 21), hours=random.randint(0, 8), minutes=random.randint(0, 59))
            lead = LeadStatus.objects.create(
                client_name=client,
                current_status=random.choice(status_templates),
                chat_room_link=f"https://chat.example.com/rooms/{client.lower().replace(' ', '-')}",
                profile=random.choice(profiles),
                is_archived=random.random() < 0.18,
                is_dummy=True,
                created_by=owner,
                last_updated_by=random.choice(users),
            )
            LeadStatus.objects.filter(pk=lead.pk).update(
                created_at=updated_at - timedelta(days=random.randint(1, 7)),
                updated_at=updated_at,
            )

        return len(clients)
