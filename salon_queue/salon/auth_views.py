from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.salon_profile
            return redirect({"owner": "owner", "receptionist": "reception", "stylist": "stylist_home"}[profile.role])
        except Exception:
            logout(request)
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                profile = user.salon_profile
                if profile.role == "stylist" and not profile.stylist_id:
                    error = "This stylist account is not linked to a stylist record."
                else:
                    login(request, user)
                    return redirect({"owner": "owner", "receptionist": "reception", "stylist": "stylist_home"}[profile.role])
            except Exception:
                error = "This account has no salon role. Ask the owner to configure it."
        else:
            error = "Incorrect username or password."
    return render(request, "salon/login.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("login")
