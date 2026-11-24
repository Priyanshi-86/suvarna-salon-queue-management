from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path("django-admin/", admin.site.urls),  # /admin is reserved for the Owner Dashboard (built later)
    path("", include("salon.urls")),
]
