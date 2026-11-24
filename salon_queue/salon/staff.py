"""Receptionist, Stylist, TV and Owner screens. Shares the same Booking table as the client side."""
import json, math, calendar
from datetime import date, time, datetime, timedelta
from django.conf import settings
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import path
from django.views.decorators.http import require_POST
from .models import Service, Stylist, Booking
from .views import now, QUEUED, OPEN_H, CLOSE_H
from .access import role_required

LANGS = ("en", "hi", "gu")
CHAIR = ("called", "serving")
err = lambda c, s=400: JsonResponse({"error": c}, status=s)
def lab(tm): return tm.strftime("%I:%M %p").lstrip("0")
def svcs(b): return [{f"name_{l}": getattr(s, f"name_{l}") for l in LANGS} for s in b.services.all()]
def mins(b): return sum(s.minutes for s in b.services.all())
def cost(b): return sum(s.price for s in b.services.all())
def body(r): return json.loads(r.body or "{}")
def occupied(st, d): return Booking.objects.filter(stylist=st, date=d, status__in=CHAIR).exists()

def sync_stylist(st):
    st.refresh_from_db()
    if st.status == "break": return
    new = "busy" if occupied(st, now().date()) else "available"
    if st.status != new: st.status = new; st.save(update_fields=["status"])

def day_rows(d):
    """Same position / wait formula as the client status page, so every screen agrees."""
    bs = list(Booking.objects.filter(date=d).exclude(status="cancelled").select_related("stylist")
              .prefetch_related("services").order_by("time", "id"))
    q = [b for b in bs if b.status in QUEUED]
    working = Stylist.objects.exclude(status="break").count() or 1
    pos, wait, acc = {}, {}, 0
    for i, b in enumerate(q):
        pos[b.pk] = i + 1; wait[b.pk] = math.ceil(acc / working); acc += mins(b)
    return [dict(id=b.pk, token=b.token, name=b.client_name, phone=b.phone, age=b.age, gender=b.gender,
                 walkin=b.is_walkin, status=b.status, time=lab(b.time), stylist=b.stylist.name if b.stylist else "",
                 stylist_id=b.stylist_id, services=svcs(b), minutes=mins(b), price=cost(b),
                 pos=pos.get(b.pk, 0), wait=wait.get(b.pk, 0)) for b in bs]

# ---------------- Receptionist ----------------
@role_required("owner", "receptionist")
def reception(request): return render(request, "salon/reception.html")

@role_required("owner", "receptionist")
def api_rqueue(request):
    td = now().date(); rows = day_rows(td)
    occ = {r["stylist_id"]: r["token"] for r in rows if r["status"] in CHAIR and r["stylist_id"]}
    sts = list(Stylist.objects.all()); sst = {s.pk: s.status for s in sts}
    for r in rows:
        r["can_call"], r["why"] = False, ""
        if r["status"] == "waiting":
            if not r["stylist_id"]: r["why"] = "nost"
            elif sst[r["stylist_id"]] == "break": r["why"] = "break"
            elif r["stylist_id"] in occ: r["why"] = "chair"
            else: r["can_call"] = True
    done = [r for r in rows if r["status"] == "done"][-5:]
    rows = [r for r in rows if r["status"] != "done"] + done
    return JsonResponse({"rows": rows,
        "stylists": [{"id": s.pk, "name": s.name, "status": s.status, "occupied": occ.get(s.pk)} for s in sts],
        "services": [{"id": s.pk, "minutes": s.minutes, "price": s.price,
                      **{f"name_{l}": getattr(s, f"name_{l}") for l in LANGS}} for s in Service.objects.all()]})

@require_POST
@role_required("owner", "receptionist")
def api_ract(request, pk):
    b = get_object_or_404(Booking, pk=pk); a = body(request).get("action"); st = b.stylist
    if a == "verify" and b.status == "booked": b.status = "waiting"
    elif a == "call" and b.status == "waiting":
        if not st: return err("nost")
        if st.status == "break": return err("break")
        if occupied(st, b.date): return err("chair")
        b.status = "called"
    elif a == "cancel" and b.status in ("booked", "waiting", "called"): b.status = "cancelled"; b.cancelled_at = now()
    elif a == "done" and b.status == "serving": b.status = "done"; b.done_at = now()
    else: return err("bad")
    b.save()
    if st: sync_stylist(st)
    return JsonResponse({"ok": True})

@require_POST
@role_required("owner", "receptionist")
def api_rstylist(request, pk):
    st = get_object_or_404(Stylist, pk=pk); to = body(request).get("status")
    if to == "break":
        if occupied(st, now().date()): return err("chair")
        st.status = "break"
    elif to == "available": st.status = "available"
    else: return err("bad")
    st.save(update_fields=["status"]); sync_stylist(st)
    return JsonResponse({"ok": True})

@role_required("owner", "receptionist")
def api_rslots(request):
    d = date.fromisoformat(request.GET["date"]); n = now(); cap = Stylist.objects.count(); out = []
    if d == n.date() and n.hour < CLOSE_H:
        out.append({"time": n.strftime("%H:%M"), "label": "now", "ok": True, "now": True})
    for h in range(OPEN_H * 2, 40):
        tm = time(h // 2, 30 * (h % 2))
        taken = Booking.objects.filter(date=d, time=tm, status__in=("booked", "waiting", "called", "serving")).count()
        past = d < n.date() or (d == n.date() and tm <= n.time())
        out.append({"time": tm.strftime("%H:%M"), "label": lab(tm), "ok": not past and taken < cap})
    return JsonResponse({"slots": out})

@require_POST
@role_required("owner", "receptionist")
def api_rbook(request):
    p = body(request); n = now(); nn = n.replace(tzinfo=None)
    try: d = date.fromisoformat(p["date"]); tm = time.fromisoformat(p["time"])
    except (KeyError, ValueError): return err("bad")
    sv = Service.objects.filter(pk__in=p.get("services", [])); st = Stylist.objects.filter(pk=p.get("stylist")).first()
    name, phone = (p.get("name") or "").strip(), (p.get("phone") or "").strip()
    if not (sv and st and name and phone): return err("bad")
    if d < n.date() or datetime.combine(d, tm) < nn - timedelta(minutes=10) or (d == n.date() and n.hour >= CLOSE_H):
        return err("closed")
    if Booking.objects.filter(stylist=st, date=d, time=tm, status__in=("booked", "waiting", "called", "serving")).exists():
        return err("taken", 409)
    try: age = int(p.get("age")) if p.get("age") else None
    except ValueError: age = None
    last = Booking.objects.filter(date=d).aggregate(m=Max("token_no"))["m"] or 0
    today = d == n.date()
    b = Booking.objects.create(client_name=name, phone=phone, age=age, gender=(p.get("gender") or "")[:1], stylist=st,
                               date=d, time=tm, token_no=last + 1, is_walkin=today, status="waiting" if today else "booked")
    b.services.set(sv)
    return JsonResponse({"id": b.pk, "token": b.token})

# ---------------- Stylist ----------------
@role_required("owner")
def stylist_pick(request):
    return render(request, "salon/stylist_pick.html", {"sts": Stylist.objects.all()})

@role_required("owner", "stylist")
def stylist_home(request):
    profile = request.user.salon_profile
    if profile.role == "owner":
        return redirect("stylist_pick")
    return render(request, "salon/stylist.html", {"st": profile.stylist})

@role_required("owner")
def stylist_view(request, name):
    st = get_object_or_404(Stylist, name__iexact=name)
    return render(request, "salon/stylist.html", {"st": st})

@role_required("owner", "stylist", own_stylist=True)
def api_stylist(request, pk):
    st = get_object_or_404(Stylist, pk=pk); td = now().date()
    bs = list(Booking.objects.filter(stylist=st, date=td, status__in=("booked", "waiting", "called", "serving"))
              .prefetch_related("services").order_by("time", "id"))
    row = lambda b: dict(id=b.pk, token=b.token, name=b.client_name, age=b.age, gender=b.gender, phone=b.phone,
                         time=lab(b.time), status=b.status, services=svcs(b), minutes=mins(b), price=cost(b))
    cur = next((b for b in bs if b.status in CHAIR), None)
    return JsonResponse({"name": st.name, "status": st.status, "current": row(cur) if cur else None,
        "schedule": [row(b) for b in bs],
        "done": Booking.objects.filter(stylist=st, date=td, status="done").count()})

@require_POST
@role_required("owner", "stylist", own_stylist=True)
def api_sact(request, pk):
    st = get_object_or_404(Stylist, pk=pk); a = body(request).get("action")
    cur = Booking.objects.filter(stylist=st, date=now().date(), status__in=CHAIR).first()
    if a == "start" and cur and cur.status == "called": cur.status = "serving"; cur.started_at = now()
    elif a == "done" and cur and cur.status == "serving": cur.status = "done"; cur.done_at = now()
    else: return err("bad")
    cur.save(); sync_stylist(st)
    return JsonResponse({"ok": True})

# ---------------- Waiting-room TV ----------------
def tv(request): return render(request, "salon/tv.html")

def api_tv(request):
    n = now(); rows = day_rows(n.date())
    chair = [r for r in rows if r["status"] in CHAIR]; q = [r for r in rows if r["status"] in QUEUED]
    for r in chair + q:
        r["est"] = None if r["status"] in CHAIR else lab((n + timedelta(minutes=r["wait"])).time())
    return JsonResponse({"rows": (chair + q)[:7]})

# ---------------- Owner ----------------
@role_required("owner")
def owner(request):
    return render(request, "salon/owner.html")


@role_required("owner")
def api_owner(request):
    n = now(); td = n.date(); nn = n.replace(tzinfo=None)
    day = list(Booking.objects.filter(date=td).select_related("stylist").prefetch_related("services"))
    kpi = {"total": len(day), "done": sum(b.status == "done" for b in day),
           "cancelled": sum(b.status == "cancelled" for b in day), "walkins": sum(b.is_walkin for b in day)}
    live = [b for b in day if b.status != "cancelled"]
    if request.GET.get("range") == "month":
        mb = Booking.objects.filter(date__year=td.year, date__month=td.month).exclude(status="cancelled")
        cnt = {}
        for b in mb: cnt[b.date.day] = cnt.get(b.date.day, 0) + 1
        chart = [{"label": str(i), "value": cnt.get(i, 0)} for i in range(1, calendar.monthrange(td.year, td.month)[1] + 1)]
    else:
        chart = [{"label": f"{h % 12 or 12}{'a' if h < 12 else 'p'}", "value": sum(b.time.hour == h for b in live)}
                 for h in range(OPEN_H, CLOSE_H)]
    month = list(Booking.objects.filter(date__year=td.year, date__month=td.month, status="done"))
    week = list(Booking.objects.filter(date__gte=td - timedelta(days=6), date__lte=td, status="done"))
    perf = []
    for s in Stylist.objects.all():
        mine = [b for b in month if b.stylist_id == s.pk]
        durs = [(b.done_at - b.started_at).total_seconds() / 60 for b in mine if b.done_at and b.started_at]
        perf.append({"name": s.name, "today": sum(b.date == td for b in mine), "month": len(mine),
                     "avg": round(sum(durs) / len(durs)) if durs else None,
                     "spark": [sum(1 for b in week if b.stylist_id == s.pk and b.date == td - timedelta(days=i)) for i in range(6, -1, -1)]})
    lim = nn + timedelta(hours=3); limt = lim.time() if lim.date() == td else time(23, 59)
    mk = lambda b: dict(token=b.token, name=b.client_name, time=lab(b.time), services=svcs(b),
                        stylist=b.stylist.name if b.stylist else "—")
    up = [mk(b) for b in sorted(day, key=lambda b: (b.time, b.pk)) if b.status in QUEUED and b.time <= limt]
    cx = [{**mk(b), "at": lab(timezone_local(b.cancelled_at).time()) if b.cancelled_at else "—"} for b in day if b.status == "cancelled"]
    return JsonResponse({"kpi": kpi, "chart": chart, "perf": perf, "upcoming": up, "cancels": cx})

def timezone_local(dt):
    from django.utils import timezone
    return timezone.localtime(dt)

urlpatterns = [
    path("reception/", reception, name="reception"),
    path("api/reception/queue/", api_rqueue),
    path("api/reception/act/<int:pk>/", api_ract),
    path("api/reception/stylist/<int:pk>/", api_rstylist),
    path("api/reception/slots/", api_rslots),
    path("api/reception/book/", api_rbook),
    path("stylist/", stylist_pick, name="stylist_pick"),
    path("my-stylist/", stylist_home, name="stylist_home"),
    path("stylist/<str:name>/", stylist_view, name="stylist"),
    path("api/stylist/<int:pk>/", api_stylist),
    path("api/stylist/<int:pk>/act/", api_sact),
    path("display/", tv, name="tv"),
    path("api/tv/", api_tv),
    path("admin/", owner, name="owner"),
    path("api/owner/", api_owner),
]
