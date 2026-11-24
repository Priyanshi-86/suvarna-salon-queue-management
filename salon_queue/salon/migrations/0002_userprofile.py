from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("salon", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("owner", "Owner"), ("receptionist", "Receptionist"), ("stylist", "Stylist")], max_length=20)),
                ("stylist", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="salon.stylist")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="salon_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
