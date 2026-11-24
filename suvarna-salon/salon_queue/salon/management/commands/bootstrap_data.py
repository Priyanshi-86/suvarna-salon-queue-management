from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from salon.models import Service, Stylist


class Command(BaseCommand):
    help = "Idempotent first-deploy seed: demo data only into an empty DB, staff accounts only if no users exist."

    def handle(self, *args, **options):
        if not Service.objects.exists() and not Stylist.objects.exists():
            call_command("load_dummy")
            call_command("load_stats")
        if not get_user_model().objects.exists():
            call_command("create_staff_accounts")
