from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from salon.models import UserProfile, Stylist

ACCOUNTS = [
    ("owner", "SuvarnaOwner#26", "owner", None),
    ("reception", "SuvarnaReception#26", "receptionist", None),
    ("priya", "SuvarnaPriya#26", "stylist", "Priya"),
    ("jils", "SuvarnaJils#26", "stylist", "Jils"),
    ("gaurang", "SuvarnaGaurang#26", "stylist", "Gaurang"),
    ("ravi", "SuvarnaRavi#26", "stylist", "Ravi"),
]

class Command(BaseCommand):
    help = "Create/update demo staff login accounts and link each to its role."

    def handle(self, *args, **options):
        User = get_user_model()
        for username, password, role, stylist_name in ACCOUNTS:
            user, _ = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.is_active = True
            user.save()
            stylist = Stylist.objects.get(name__iexact=stylist_name) if stylist_name else None
            UserProfile.objects.update_or_create(
                user=user, defaults={"role": role, "stylist": stylist}
            )
            self.stdout.write(f"{username} | {password} | {role}")
