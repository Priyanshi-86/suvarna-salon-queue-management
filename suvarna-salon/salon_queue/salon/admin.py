from django.contrib import admin
from .models import Service, Stylist, Booking
admin.site.register(Service)
@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ("name", "status"); list_editable = ("status",)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("token_no", "client_name", "date", "time", "stylist", "status")
    list_editable = ("status",); list_filter = ("date", "status")
