import json, math
from datetime import date, time
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Service, Stylist, Booking

DEMO_PHONE = "9876500001"          # the demo client whose history is pre-loaded
OPEN_H, CLOSE_H = 10, 20           # salon hours 10 AM - 8 PM
ONLINE_CUTOFF = time(19, 30)       # online booking closes 30 min before closing
ACTIVE = ("booked", "waiting", "called", "serving")
QUEUED = ("booked", "waiting")

def now(): return timezone.localtime()
def phone_of(r): return r.session.get("phone", DEMO_PHONE)
def mine(r):
    return (Booking.objects.filter(phone=phone_of(r)).select_related("stylist")
            .prefetch_related("services").order_by("-date", "-time"))

def home(request):
    n = now(); rows = list(mine(request))
    prev = [b for b in rows if b.status in ("done", "cancelled") or b.date < n.date()][:6]
    current = next((b for b in rows if b.date == n.date() and b.is_active), None)
    return render(request, "salon/home.html", {
        "is_open": OPEN_H <= n.hour < CLOSE_H, "prev": prev, "current": current,
        "phone": "+91 98765 43210", "area": "Satellite, Ahmedabad"})

def book(request):
    boot = {"services": [{"id": s.id, "glyph": s.glyph, "minutes": s.minutes, "price": s.price,
                          **{f"{k}_{l}": getattr(s, f"{k}_{l}") for k in ("name", "desc") for l in ("en", "hi", "gu")}}
                         for s in Service.objects.all()],
            "stylists": [{"id": x.id, "name": x.name, "status": x.status} for x in Stylist.objects.all()],
            "name": request.session.get("name", ""), "phone": request.session.get("phone", "")}
    return render(request, "salon/book.html", {"boot": boot})

def my_bookings(request):
    n = now(); rows = list(mine(request))
    cur = [b for b in rows if b.date == n.date() and b.is_active]
    up = [b for b in rows if b.date > n.date() and b.status == "booked"]
    prev = [b for b in rows if b not in cur and b not in up]
    return render(request, "salon/my_bookings.html", {"cur": cur, "up": up, "prev": prev})

def status(request, pk):
    get_object_or_404(Booking, pk=pk)
    return render(request, "salon/status.html", {"pk": pk})

def api_slots(request):
    d = date.fromisoformat(request.GET["date"]); n = now()
    closed = d < n.date() or (d == n.date() and n.time() >= ONLINE_CUTOFF)
    cap = Stylist.objects.count(); out = []
    for h in range(OPEN_H * 2, 40):                      # 10:00 ... 19:30
        tm = time(h // 2, 30 * (h % 2))
        taken = Booking.objects.filter(date=d, time=tm, status__in=ACTIVE).count()
        past = d == n.date() and tm <= n.time()
        out.append({"time": tm.strftime("%H:%M"), "label": tm.strftime("%I:%M %p").lstrip("0"),
                    "ok": not (closed or past) and taken < cap})
    return JsonResponse({"closed": closed, "slots": out})

def api_stylists(request):
    d = date.fromisoformat(request.GET["date"]); tm = time.fromisoformat(request.GET["time"])
    today = d == now().date()
    return JsonResponse([{"id": s.id, "name": s.name, "status": s.status if today else "available",
                          "booked": Booking.objects.filter(stylist=s, date=d, time=tm, status__in=ACTIVE).exists()}
                         for s in Stylist.objects.all()], safe=False)

@require_POST
def api_book(request):
    p = json.loads(request.body); n = now()
    try: d = date.fromisoformat(p["date"]); tm = time.fromisoformat(p["time"])
    except (KeyError, ValueError): return JsonResponse({"error": "bad"}, status=400)
    svcs = Service.objects.filter(pk__in=p.get("services", []))
    st = Stylist.objects.filter(pk=p.get("stylist")).first()
    name, phone = (p.get("name") or "").strip(), (p.get("phone") or "").strip()
    if not (svcs and st and name and phone): return JsonResponse({"error": "bad"}, status=400)
    if d < n.date() or (d == n.date() and (tm <= n.time() or n.time() >= ONLINE_CUTOFF)):
        return JsonResponse({"error": "closed"}, status=400)
    if Booking.objects.filter(stylist=st, date=d, time=tm, status__in=ACTIVE).exists():
        return JsonResponse({"error": "taken"}, status=409)
    last = Booking.objects.filter(date=d).aggregate(m=Max("token_no"))["m"] or 0
    b = Booking.objects.create(client_name=name, phone=phone, stylist=st, date=d, time=tm, token_no=last + 1)
    b.services.set(svcs)
    request.session["name"], request.session["phone"] = name, phone
    return JsonResponse({"id": b.pk})

def api_status(request, pk):
    b = get_object_or_404(Booking, pk=pk); pos = wait = 0
    if b.status in QUEUED:
        q = list(Booking.objects.filter(date=b.date, status__in=QUEUED).order_by("time", "id"))
        ahead = q[:q.index(b)] if b in q else []
        working = Stylist.objects.exclude(status="break").count() or 1
        pos, wait = len(ahead) + 1, math.ceil(sum(x.total_minutes for x in ahead) / working)
    return JsonResponse({"token": b.token, "state": b.status, "position": pos, "wait": wait,
                         "stylist": b.stylist.name if b.stylist else "", "price": b.total_price,
                         "minutes": b.total_minutes,
                         "services": [{f"name_{l}": getattr(s, f"name_{l}") for l in ("en", "hi", "gu")} for s in b.services.all()]})

@require_POST
def api_cancel(request, pk):
    b = get_object_or_404(Booking, pk=pk)
    if b.status not in QUEUED: return JsonResponse({"error": "locked"}, status=400)
    b.status = "cancelled"; b.cancelled_at = timezone.now(); b.save(update_fields=["status", "cancelled_at"])
    return JsonResponse({"ok": True})
