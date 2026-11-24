Suvarna Salon — Django booking, reception, stylist, owner dashboard and public TV

SETUP
  pip install django
  python manage.py migrate
  python manage.py load_dummy
  python manage.py load_stats
  python manage.py create_staff_accounts
  python manage.py runserver 0.0.0.0:8000

Open the staff sign-in page at http://127.0.0.1:8000/login/.
The role is assigned to each account in the database. Do not type a role in the URL.
After login, the app opens the correct dashboard automatically.

SCREENS
  Public customer website: /  /book_appoinment/  /my_bookings/  /status/<id>/
  Staff login:             /login/
  Owner dashboard:         /admin/
  Receptionist workspace:  /reception/
  Stylist workspace:       /my-stylist/  (automatically linked to the logged-in stylist)
  Waiting-room TV:         /display/  (public; no login required)
  Django admin:            /django-admin/

DEMO STAFF ACCOUNTS
  Role         Username       Password
  Owner        owner          SuvarnaOwner#26
  Reception    reception      SuvarnaReception#26
  Stylist      priya          SuvarnaPriya#26
  Stylist      jils           SuvarnaJils#26
  Stylist      gaurang        SuvarnaGaurang#26
  Stylist      ravi           SuvarnaRavi#26

Each stylist account is linked to the matching Stylist database record. To recreate
or reset these demo accounts after running migrations and load_dummy:
  python manage.py create_staff_accounts

ACCESS RULES
  - Owner can open the owner dashboard, reception workspace and stylist list.
  - Receptionist can open reception only.
  - A stylist can open only their own workspace and their own stylist data endpoints.
  - Staff-only pages and APIs require a valid login and role.
  - /display/ and /api/tv/ remain public for the waiting-room screen.
  - The owner PIN has been removed; owner uses the same login page as other staff.

SECURITY NOTE
  These are development/demo passwords. Change them before exposing the site to the
  internet. Use DEBUG=False, a private SECRET_KEY and a restricted ALLOWED_HOSTS list
  for production deployment.

DEMO CLIENT PHONE
  9876500001
