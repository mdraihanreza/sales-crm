from django.core.management.base import BaseCommand
from django.db import transaction

from users.demo_data import cleanup_demo_data


class Command(BaseCommand):
    help = "Remove all safely tagged demo data without affecting real users or configuration."

    def handle(self, *args, **options):
        with transaction.atomic():
            deleted = cleanup_demo_data()

        self.stdout.write(self.style.SUCCESS("Demo data cleaned successfully."))
        for key, value in deleted.items():
            self.stdout.write(f"{key}: {value}")
