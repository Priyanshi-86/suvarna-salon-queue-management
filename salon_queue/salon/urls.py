from django.urls import path
from . import views as v
from .auth_views import login_view, logout_view
urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", v.home, name="home"),
    path("book_appoinment/", v.book, name="book"),
    path("my_bookings/", v.my_bookings, name="my_bookings"),
    path("status/<int:pk>/", v.status, name="status"),
    path("api/slots/", v.api_slots),
    path("api/stylists/", v.api_stylists),
    path("api/book/", v.api_book),
    path("api/status/<int:pk>/", v.api_status),
    path("api/cancel/<int:pk>/", v.api_cancel),
]

from .staff import urlpatterns as _staff
urlpatterns += _staff
