import random
from datetime import datetime, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from salon.models import Service, Stylist, Booking

NAMES = ["Aarav Shah", "Diya Patel", "Vihaan Mehta", "Anaya Joshi", "Kabir Desai", "Myra Trivedi", "Reyansh Pandya",
         "Saanvi Bhatt", "Ishaan Modi", "Tara Vyas", "Yash Thakkar", "Riya Parekh"]

class Command(BaseCommand):
    help = "Add extra dummy history (last 30 days + a few done/cancelled today) for the Owner dashboard. Run after load_dummy."
    def handle(self, *a, **o):
        sv, sts = list(Service.objects.all()), list(Stylist.objects.all())
        if not sv or not sts: return self.stdout.write("Run load_dummy first.")
        random.seed(7); today = timezone.localdate(); aware = lambda d, t: timezone.make_aware(datetime.combine(d, t))
        def make(d, tok, tm, status, walkin):
            picks = random.sample(sv, random.choice([1, 1, 2])); mins = sum(s.minutes for s in picks)
            b = Booking.objects.create(client_name=random.choice(NAMES), phone=f"90000{random.randint(10000,99999)}",
                stylist=random.choice(sts), date=d, time=tm, status=status, is_walkin=walkin, token_no=tok,
                age=random.randint(18, 60), gender=random.choice("mf"))
            b.services.set(picks)
            if status == "done":
                b.started_at = aware(d, tm); b.done_at = b.started_at + timedelta(minutes=max(10, mins + random.randint(-5, 10)))
            if status == "cancelled": b.cancelled_at = aware(d, tm) - timedelta(minutes=random.randint(20, 120))
            b.save()
        for back in range(1, 31):
            d = today - timedelta(days=back)
            for k in range(random.randint(6, 14)):
                tm = time(random.randint(10, 19), random.choice([0, 30]))
                make(d, k + 20, tm, "cancelled" if random.random() < .1 else "done", random.random() < .3)
        for k, tm in enumerate([time(10, 0), time(10, 0), time(10, 30), time(10, 30), time(10, 30)]):
            make(today, k + 1, tm, "done", k % 3 == 0)
        for k, tm in enumerate([time(10, 30), time(11, 0)]): make(today, 6 + k, tm, "cancelled", False)
        self.stdout.write(self.style.SUCCESS("Extra stats loaded."))
