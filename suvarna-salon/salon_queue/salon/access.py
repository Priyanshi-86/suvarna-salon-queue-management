from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

def role_required(*roles, own_stylist=False):
    def decorate(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.path.startswith("/api/"):
                    return JsonResponse({"error": "login_required"}, status=401)
                return redirect(f"{reverse('login')}?next={request.path}")
            try:
                profile = request.user.salon_profile
            except Exception:
                if request.path.startswith("/api/"):
                    return JsonResponse({"error": "role_required"}, status=403)
                return redirect("login")
            allowed = profile.role in roles
            if own_stylist and profile.role == "stylist":
                allowed = profile.stylist_id is not None and str(profile.stylist_id) == str(kwargs.get("pk"))
            if not allowed:
                if request.path.startswith("/api/"):
                    return JsonResponse({"error": "forbidden"}, status=403)
                target = {"owner": "owner", "receptionist": "reception", "stylist": "stylist_home"}.get(profile.role, "login")
                return redirect(target)
            return view(request, *args, **kwargs)
        return wrapped
    return decorate
