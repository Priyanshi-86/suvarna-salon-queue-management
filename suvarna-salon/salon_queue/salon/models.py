from django.db import models
from django.db.models import Sum

class Service(models.Model):
    name_en = models.CharField(max_length=80); name_hi = models.CharField(max_length=80); name_gu = models.CharField(max_length=80)
    desc_en = models.CharField(max_length=200); desc_hi = models.CharField(max_length=200); desc_gu = models.CharField(max_length=200)
    minutes = models.PositiveIntegerField(); price = models.PositiveIntegerField()
    glyph = models.CharField(max_length=4, default="✂")
    def __str__(self): return self.name_en

class Stylist(models.Model):
    STATUS = [("available", "Available"), ("busy", "Busy"), ("break", "On break")]
    name = models.CharField(max_length=60)
    status = models.CharField(max_length=10, choices=STATUS, default="available")
    def __str__(self): return self.name

class Booking(models.Model):
    STATUS = [("booked", "Booked"), ("waiting", "Waiting"), ("called", "Called"),
              ("serving", "Serving"), ("done", "Done"), ("cancelled", "Cancelled")]
    client_name = models.CharField(max_length=80); phone = models.CharField(max_length=15)
    services = models.ManyToManyField(Service)
    stylist = models.ForeignKey(Stylist, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(); time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS, default="booked")
    is_walkin = models.BooleanField(default=False)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    token_no = models.PositiveIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["date", "time", "id"]
    @property
    def token(self): return f"S-{self.token_no}"
    @property
    def is_active(self): return self.status in ("booked", "waiting", "called", "serving")
    @property
    def total_minutes(self): return self.services.aggregate(m=Sum("minutes"))["m"] or 0
    @property
    def total_price(self): return self.services.aggregate(p=Sum("price"))["p"] or 0
    def __str__(self): return f"{self.token} {self.client_name}"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("receptionist", "Receptionist"),
        ("stylist", "Stylist"),
    ]
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="salon_profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    stylist = models.ForeignKey(Stylist, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
