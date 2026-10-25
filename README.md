# AutoLedger BD — ARONNO Edition 🇧🇩
### বাংলাদেশের গাড়ির খরচ ও রক্ষণাবেক্ষণ ব্যবস্থাপনা

**A Django/PostgreSQL-ready, responsive, installable PWA that closely follows the user's chosen white-and-green AutoLedger BD desktop/mobile reference.** Source code and working Django views/models/forms are included; `design_preview.html` is a separate static *sample-data* visualization of the dashboard.

## Start here — Windows, no Docker needed

1. Install **Python 3.11–3.13** from python.org. During installation, choose **Add python.exe to PATH**.
2. Extract the ZIP into a normal writable folder, e.g. `C:\Users\You\Downloads\AutoLedger_BD_Reference_PWA`.
3. Double-click **`setup_windows.bat`**. It creates the Python environment, installs packages and builds the database (defaults to SQLite for simpler local setup).
4. Double-click **`start_windows.bat`** to run the development server.
5. Open **http://127.0.0.1:8000/register/** in Chrome or Edge and register your own account. Or create a superadmin with the command below.

Optional commands in Windows PowerShell, opened inside the extracted project folder:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_demo --username YOUR_USERNAME
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

The `seed_demo` command inserts fictional sample records into **your chosen existing account only**. Skip it to start with empty records. Django admin is at `http://127.0.0.1:8000/admin/`.

**Want to inspect the look first without installing Python?** Double-click `design_preview.html` in the extracted folder. This is a static dashboard design preview with illustrative numbers, **not** the database-backed application. The live app has the same new CSS and page layout, but values come from your own records.

## Included features

- **Reference-aligned UI/UX:** bright white sidebar, Bangladesh green highlights, four tinted financial summary tiles, compact line and doughnut charts, spending per vehicle, recent expenses, upcoming reminders and vehicle card; a distinct smartphone layout, floating add action and bottom tabs.
- **ARONNO signature:** sidebar, site footer, login visual and app information.
- **Bangladesh-first:** Bangla defaults, English option, Bangladeshi Taka **৳**, local number plate entry, Bangladesh examples and fuel categories **Octane, Petrol, Diesel, CNG, LPG and Electric**.
- **Cars:** create, edit, view details, upload a car photo, plate, model year and odometer, view car history and reminders.
- **Expenses:** fuel, maintenance, trip costs, toll, parking, wash, tax token, BRTA fitness, insurance and more. Edit, delete, filter and search.
- **Refuelling:** form includes tappable fuel-type chips, date, quantity, cost, odometer, location and **two separate uploaded photos** (receipt and pump-meter). Stored against the correct owner and car.
- **Drivers:** add or edit drivers with a Bangladesh phone number, optional licence number and one assigned vehicle.
- **Reminders:** date- and odometer-based renewals for fitness, tax tokens, engine oil, insurance etc.; mark completed or reopen.
- **Reports:** lifetime and monthly graphs, category totals, fuel usage breakdown and one-click UTF-8 Excel-friendly CSV export.
- **Accounts:** registration/login, personal settings, CSRF-protected form actions, owner-based access controls and protected object lookups.
- **Progressive Web App (PWA):** responsive site with install page, manifest, app icons and service worker that caches only public static assets, not personal records. Install instructions cover Android Chrome, iPhone Safari and desktop Chrome/Edge.
- **PostgreSQL + Docker:** support via environment variables and `docker-compose.yml`; SQLite is the convenience default for Windows setup.

## PWA installation on Android / iPhone / Windows

For installation on a phone, **publish the app on a real HTTPS domain first**. Visiting a laptop's `http://192.168...` development IP is not enough for standard PWA installation. Then:

- Android: open the live URL in Chrome → **Install app** or **Add to Home screen**.
- iPhone: open the URL in **Safari** → Share → **Add to Home Screen**.
- Windows / Mac: Chrome or Edge → browser address bar install icon or browser menu → Install App.

Inside the site, click **Install App** in the sidebar and follow device-specific instructions. The installed app syncs with your hosted Django database while online.

**Important:** This is an installable **PWA**, not a native `.apk`, `.ipa`, or Windows `.exe` file. No Play Store publication, SMS/WhatsApp reminders, background GPS, OCR receipt recognition or offline editing is included. PWA installation depends on the device/browser and HTTPS; there is no universal forced download button.

## PostgreSQL / Docker

For Docker Desktop users, start Docker Desktop (ensure WSL integration and Docker Engine are on), then:

```bash
cp .env.example .env
# Set a unique DJANGO_SECRET_KEY and DB_PASSWORD in .env.
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

On Windows without a Unix `cp` command, copy `.env.example` to `.env` in File Explorer or use `copy .env.example .env` in CMD. The Docker development server is at http://127.0.0.1:8000/.

For local PostgreSQL without Docker, set `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` in `.env`. SQLite is used only when `DB_HOST` is unset.

## macOS / Linux quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Testing, limits and deployment precautions

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

Project includes `0001_initial.py` and `0002_driver_trip.py` migrations and Python/Django tests for tenant isolation, private records, POST-only deletes, PWA endpoints, trip filtering and driver/vehicle privacy.

**Verification disclosure:** Source files have passed Python syntax compilation, JavaScript syntax checks, dashboard preview HTML/JSON parsing, stylesheet parsing and template-tag balance checks. **Full Django runtime and browser visual tests were not performed in the file creation environment**, because network/package installation and browser navigation were unavailable there. Run the listed Django checks and tests after installing dependencies locally before deployment. Minor visual differences (fonts and the user's real photos/data) are expected compared with the supplied mockup; this is not a guaranteed pixel-perfect bitmap clone.

Production needs a secure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, correct `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, HTTPS reverse proxy, durable image storage, backups, rate limiting and mail/password recovery. Uploaded files have 8 MB and file-type limits; do not treat this project as independently security-audited. Personal data should not be tested with genuine records until deployment and policies are ready.

## Project structure

- `ledger/models.py`, `ledger/forms.py`, `ledger/views.py`: domain objects and CRUD/security logic.
- `templates/base.html`, `templates/ledger/dashboard.html`: close-to-reference website shell and dashboard.
- `templates/ledger/*`: cars, detail, fuel/expense form, reminders, drivers, reports, documents, installation and settings.
- `static/css/reference.css`: exact-reference-focused desktop/mobile styles, loaded after the base UI sheet.
- `static/js/app.js`, `static/js/reference.js`: interactive charts, installed app logic and photo/fuel controls.
- `static/img/demo-car.jpg`: demonstration crop from the user's approved concept design. Upload real car photos to replace it.
- `design_preview.html`: static reference-layout preview, illustrative data only.

**Made for Bangladesh · Designed & signed by ARONNO**
# Account roles and driver login

- **Superuser:** manages all users and database records through `/admin/`. Create your superuser with `.venv\Scripts\python.exe manage.py createsuperuser` if you do not have one yet.
- **Admin:** a regular registered app account manages its own cars, expenses, reminders and drivers. App admins do not receive Django staff or superuser privileges.
- **Driver:** an admin opens **Drivers → Add Driver**, enters the profile, assigns a car, and creates a unique username and password. The driver uses those credentials at `/login/` and sees a dedicated dashboard for the assigned car. Driver expense submissions appear in the owning admin's records, with the submitting account recorded.

Use **Drivers → Edit** to change an assignment, reset a password, or turn off **Allow this driver to log in**. Blank password fields preserve the existing password. Existing driver profiles need to be edited once to create login credentials. Deleting a driver profile disables its login account.

Sessions expire after **5 minutes of inactivity** and use browser-session cookies. The app returns an idle user to login, and the server also checks inactivity on every request. Activity in another app tab keeps the shared session active. Closing the entire browser normally clears the login cookie; browser session-restore features may restore it, but the server's five-minute inactivity limit still applies.

The driver-account migration preserves existing vehicles, expenses and accounts. A database backup made before this change is stored locally at `.backups/before-driver-login.sqlite3`.

# Mobile expense notifications

Each newly created expense sends an in-app notification to its fleet admin and active superusers. Editing an expense does not send a second notification. Open the header bell to read alerts and **Settings → Mobile expense notifications → Enable on this device** to enable phone alerts. Each recipient must enable their own phone and allow the browser's notification permission. Notification taps open the relevant alert after login. Detailed expense information is kept off the phone's lock screen.

Mobile Web Push requires the deployed app to use **HTTPS**. On iPhone/iPad (iOS/iPadOS 16.4 or later), add the app to the Home Screen first. A localhost development server can test browser APIs on the same computer; a phone visiting a plain HTTP LAN address cannot enable Web Push.

Web Push uses `pywebpush`. Local signing keys have been created in `.secrets/`, which is excluded from Git and Docker. Keep these keys persistent when deploying, or supply `WEBPUSH_PRIVATE_KEY` and `WEBPUSH_PUBLIC_KEY` through the server environment. Run `python manage.py setup_webpush` to create keys for a new installation and restart Django afterward. Set `WEBPUSH_SUBJECT` to your real contact email, for example `mailto:you@yourdomain.com`. Do not rotate keys casually: existing devices would need to enable notifications again.

Push is attempted after the expense transaction commits. A delivery failure does not undo the expense or the in-app alert. Pending deliveries can be retried with `python manage.py retry_push_notifications`; schedule this command if automatic retries are needed. Expired subscriptions are removed when the push provider reports them. Phone delivery still depends on the device's notification permission, internet connection and operating system. No real-phone delivery has been tested from this local environment.

