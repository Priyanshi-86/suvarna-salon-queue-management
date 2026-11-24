from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from salon.models import Service, Stylist, Booking
from salon.views import DEMO_PHONE

class Command(BaseCommand):
    help = "Load dummy salon data"
    def handle(self, *a, **o):
        Booking.objects.all().delete(); Service.objects.all().delete(); Stylist.objects.all().delete()
        S = lambda en, hi, gu, de, dh, dg, m, p, g: Service.objects.create(
            name_en=en, name_hi=hi, name_gu=gu, desc_en=de, desc_hi=dh, desc_gu=dg, minutes=m, price=p, glyph=g)
        hc = S("Haircut", "हेयरकट", "હેરકટ", "Precision cut and blow-dry, styled to your face shape.",
               "सटीक कट और ब्लो-ड्राई, आपके चेहरे के अनुसार स्टाइल।", "ચોક્કસ કટ અને બ્લો-ડ્રાય, તમારા ચહેરા મુજબ સ્ટાઇલ.", 30, 400, "✂")
        bt = S("Beard trim", "दाढ़ी ट्रिम", "દાઢી ટ્રિમ", "Shaping and clean edges with a hot-towel finish.",
               "आकार और साफ़ किनारे, गर्म तौलिये के साथ।", "આકાર અને સાફ કિનારી, ગરમ ટુવાલ સાથે.", 15, 200, "🪒")
        fa = S("Facial", "फेशियल", "ફેશિયલ", "Deep cleanse, exfoliation and massage for glowing skin.",
               "गहरी सफ़ाई, एक्सफ़ोलिएशन और मसाज, चमकती त्वचा के लिए।", "ઊંડી સફાઈ, એક્સફોલિએશન અને મસાજ, ચમકતી ત્વચા માટે.", 45, 900, "✦")
        hcol = S("Hair colour", "हेयर कलर", "હેર કલર", "Ammonia-free colour with a gloss treatment.",
                 "अमोनिया-मुक्त रंग और ग्लॉस ट्रीटमेंट।", "એમોનિયા-મુક્ત રંગ અને ગ્લોસ ટ્રીટમેન્ટ.", 90, 1800, "◐")
        hm = S("Head massage", "हेड मसाज", "હેડ મસાજ", "Relaxing oil massage for scalp and shoulders.",
               "सिर और कंधों के लिए आरामदायक तेल मसाज।", "માથા અને ખભા માટે આરામદાયક તેલ મસાજ.", 20, 300, "❋")
        pr, ji, ga, ra = [Stylist.objects.create(name=n, status=s) for n, s in
                          [("Priya", "available"), ("Jils", "busy"), ("Gaurang", "break"), ("Ravi", "available")]]
        today = timezone.localdate()
        # Today's queue: tokens S-10..S-13 ahead, demo client is S-14 (5th in line)
        queue = [("Anita Shah", [hc], pr), ("Rohan Mehta", [bt], ra), ("Kavya Patel", [hc], ji), ("Dev Joshi", [bt], pr),
                 ("Meera Desai", [hc], ra), ("Neha Trivedi", [hc, bt], pr), ("Karan Thakkar", [fa], ra), ("Isha Bhatt", [hm], ji)]
        for i, (name, sv, st) in enumerate(queue):
            b = Booking.objects.create(client_name=name, phone=DEMO_PHONE if name == "Neha Trivedi" else f"98250000{i:02d}",
                                       stylist=st, date=today, time=time(11 + i // 2, 30 * (i % 2)),
                                       status="waiting" if i % 2 else "booked", token_no=10 + i)
            b.services.set(sv)
        # History + one upcoming booking for the demo client
        hist = [(-3, "done", [hc, bt], pr), (-10, "done", [fa], ji), (-17, "cancelled", [hcol], ra),
                (-24, "done", [hm], pr), (-38, "done", [hc], ra), (2, "booked", [hc], pr)]
        for k, (off, stt, sv, st) in enumerate(hist):
            b = Booking.objects.create(client_name="Neha Trivedi", phone=DEMO_PHONE, stylist=st,
                                       date=today + timedelta(days=off), time=time(12 + k % 4, 0), status=stt, token_no=3 + k)
            b.services.set(sv)
        self.stdout.write(self.style.SUCCESS("Dummy data loaded. Demo client phone: " + DEMO_PHONE))
