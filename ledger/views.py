import calendar
import csv
import json
from collections import defaultdict
from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import RegisterForm, VehicleForm, ExpenseForm, ReminderForm, DriverForm
from .models import Vehicle, Expense, Reminder, Driver, CATEGORY_CHOICES, FUEL_CHOICES
from .context import TRANSLATIONS
from .access import is_driver, available_vehicles
from django.db import transaction


@login_required
@require_POST
def session_activity(request):
    return HttpResponse(status=204)


def localize_form(form, request):
    """Use the selected Bangla/English language for the main form field labels."""
    locale = TRANSLATIONS.get(request.session.get('app_language', 'bn'), TRANSLATIONS['bn'])
    labels = {
        'name':'name', 'brand':'brand', 'model_year':'year', 'plate':'plate',
        'fuel_type':'fuel_type', 'odometer':'odometer', 'color':'colour',
        'photo':'photo', 'vehicle':'vehicle', 'category':'category',
        'description':'description', 'amount':'amount', 'date':'date',
        'location':'location', 'quantity':'quantity', 'notes':'notes',
        'receipt_photo':'receipt', 'meter_photo':'meter_photo',
        'due_date':'due_date', 'due_odometer':'due_km',
    }
    for name, key in labels.items():
        if name in form.fields:
            form.fields[name].label = locale.get(key, form.fields[name].label)
    if 'title' in form.fields:
        form.fields['title'].label = 'রিমাইন্ডারের নাম' if request.session.get('app_language','bn') == 'bn' else 'Reminder Title'
    return form



def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to AutoLedger BD! Add your first car to begin.')
        return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})


def summarize(qs):
    sums = {k: Decimal('0') for k in ['FUEL','MAINTENANCE','OTHER']}
    for row in qs.values('category').annotate(total=Sum('amount')):
        key = row['category'] if row['category'] in ('FUEL', 'MAINTENANCE') else 'OTHER'
        sums[key] += row['total'] or 0
    sums['TOTAL'] = sum(sums.values())
    return sums


def make_months(n=8):
    today = timezone.localdate()
    result = []
    for i in reversed(range(n)):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        result.append((year, month))
    return result


def chart_data(qs, n=8):
    periods = make_months(n)
    by_month = defaultdict(lambda: {'fuel': 0, 'maintenance': 0, 'other': 0})
    start = date(*periods[0], 1)
    for row in qs.filter(date__gte=start).values('date', 'category').annotate(total=Sum('amount')):
        m = row['date'].strftime('%Y-%m')
        key = row['category'].lower() if row['category'] in ('FUEL', 'MAINTENANCE') else 'other'
        by_month[m][key] += float(row['total'] or 0)
    return {
        'labels': [calendar.month_abbr[m] for _,m in periods],
        'fuel': [by_month[f'{y}-{m:02}']['fuel'] for y,m in periods],
        'maintenance': [by_month[f'{y}-{m:02}']['maintenance'] for y,m in periods],
        'other': [by_month[f'{y}-{m:02}']['other'] for y,m in periods],
    }


def breakdown(qs):
    results = dict(qs.values_list('fuel_type').annotate(total=Sum('amount')))
    labels = [('OCTANE','Octane','#00865c'),('PETROL','Petrol','#ef5350'),
              ('DIESEL','Diesel','#316ef6'),('CNG','CNG','#ffb020'),
              ('LPG','LPG','#9867e8'),('ELECTRIC','Electric','#18aaa8')]
    total = float(sum(results.values(), Decimal(0))) if results else 0
    output = []
    for key, name, color in labels:
        v = float(results.get(key) or 0)
        if v:
            output.append({'name': name, 'value': v, 'percent': round(v / total * 100) if total else 0, 'color': color})
    return output


@login_required
def dashboard(request):
    if is_driver(request.user):
        driver = Driver.objects.filter(user=request.user).select_related('assigned_vehicle', 'owner').first()
        car = available_vehicles(request.user).first()
        records = Expense.objects.filter(vehicle=car, owner=driver.owner).select_related('submitted_by') if car and driver else Expense.objects.none()
        return render(request, 'ledger/driver_dashboard.html', {
            'section':'dashboard', 'driver':driver, 'car':car, 'records':records[:20],
            'driver_total':records.aggregate(total=Sum('amount'))['total'] or 0,
        })
    qs = Expense.objects.filter(owner=request.user)
    today = timezone.localdate()
    month = qs.filter(date__year=today.year, date__month=today.month)
    totals = summarize(month)
    all_vehicles = list(Vehicle.objects.filter(owner=request.user))
    fuel = breakdown(month.filter(category='FUEL'))
    by_car = list(qs.filter(date__year=today.year, date__month=today.month).values('vehicle__name', 'vehicle_id').annotate(total=Sum('amount')).order_by('-total')[:4])
    upcoming = list(Reminder.objects.filter(owner=request.user, done=False).select_related('vehicle').order_by('due_date')[:5])
    ctx = {
        'section': 'dashboard', 'totals': totals, 'vehicles': all_vehicles,
        'by_car': by_car, 'fuel_breakdown': fuel,
        'recent': month.select_related('vehicle')[:6],
        'upcoming': upcoming, 'month_label': today.strftime('%B %Y'),
        'chart': chart_data(qs), 'vehicle_count': len(all_vehicles),
        'total_car_spend': float(sum((r['total'] for r in by_car), Decimal(0))) if by_car else 0,
    }
    return render(request, 'ledger/dashboard.html', ctx)


@login_required
def vehicles(request):
    cars = Vehicle.objects.filter(owner=request.user)
    cars = cars.annotate(total_spent=Sum('expenses__amount'))
    return render(request, 'ledger/vehicles.html', {'section': 'vehicles', 'cars': cars})


@login_required
def vehicle_form(request, pk=None):
    obj = get_object_or_404(Vehicle, pk=pk, owner=request.user) if pk else None
    form = VehicleForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        car = form.save(commit=False)
        car.owner = request.user
        car.save()
        messages.success(request, 'Vehicle saved successfully.')
        return redirect('vehicles')
    localize_form(form, request)
    return render(request, 'ledger/form.html', {'form': form, 'section': 'vehicles',
        'form_title': 'Edit Vehicle' if obj else 'Add Vehicle', 'back_url': 'vehicles', 'form_kind': 'vehicle'})


@login_required
@require_POST
def vehicle_delete(request, pk):
    car = get_object_or_404(Vehicle, pk=pk, owner=request.user)
    car.delete()
    messages.success(request, 'Vehicle deleted.')
    return redirect('vehicles')


@login_required
def expenses(request):
    qs = Expense.objects.filter(owner=request.user).select_related('vehicle')
    category = request.GET.get('category', '')
    if category in dict(CATEGORY_CHOICES):
        qs = qs.filter(category=category)
    car = request.GET.get('vehicle', '')
    if car.isdigit():
        qs = qs.filter(vehicle_id=int(car))
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(description__icontains=search) | Q(location__icontains=search) |
                       Q(vehicle__name__icontains=search) | Q(vehicle__plate__icontains=search))
    return render(request, 'ledger/expenses.html', {'section': 'fuel' if category == 'FUEL' else 'maintenance' if category == 'MAINTENANCE' else 'trips' if category == 'TRIP' else 'expenses', 'records': qs[:200],
        'sum_amount': qs.aggregate(total=Sum('amount'))['total'] or 0, 'categories': CATEGORY_CHOICES,
        'cars': Vehicle.objects.filter(owner=request.user), 'chosen_category': category,
        'chosen_vehicle': car, 'query': search})


@login_required
@transaction.atomic
def expense_form(request, pk=None):
    obj = get_object_or_404(Expense, pk=pk, owner=request.user) if pk else None
    initial = {}
    if not pk:
        if request.GET.get('category') in dict(CATEGORY_CHOICES):
            initial['category'] = request.GET['category']
        initial['date'] = timezone.localdate()
    form = ExpenseForm(request.POST or None, request.FILES or None,
                       instance=obj, owner=request.user, initial=initial)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.owner = record.vehicle.owner
        if not record.pk:
            record.submitted_by = request.user
        record.save()
        if record.odometer and record.odometer > record.vehicle.odometer:
            record.vehicle.odometer = record.odometer
            record.vehicle.save(update_fields=['odometer'])
        messages.success(request, 'Expense saved successfully.')
        return redirect('dashboard' if is_driver(request.user) else 'expenses')
    localize_form(form, request)
    return render(request, 'ledger/form.html', {'form': form, 'section': 'expenses',
        'form_title': 'Edit Expense' if obj else 'Add Expense', 'back_url': 'dashboard' if is_driver(request.user) else 'expenses', 'form_kind': 'expense',
        'has_cars': available_vehicles(request.user).exists(), 'initial_category':obj.category if obj else initial.get('category','')})


@login_required
@require_POST
def expense_delete(request, pk):
    obj = get_object_or_404(Expense, pk=pk, owner=request.user)
    obj.delete()
    messages.success(request, 'Expense deleted.')
    return redirect('expenses')


@login_required
def reminders(request):
    qs = Reminder.objects.filter(owner=request.user).select_related('vehicle')
    status = request.GET.get('status', 'active')
    if status == 'active':
        qs = qs.filter(done=False)
    elif status == 'completed':
        qs = qs.filter(done=True)
    return render(request, 'ledger/reminders.html', {'section': 'reminders', 'items': qs, 'status': status})


@login_required
def reminder_form(request, pk=None):
    obj = get_object_or_404(Reminder, pk=pk, owner=request.user) if pk else None
    form = ReminderForm(request.POST or None, instance=obj, owner=request.user)
    if request.method == 'POST' and form.is_valid():
        reminder = form.save(commit=False)
        reminder.owner = request.user
        reminder.save()
        messages.success(request, 'Reminder saved.')
        return redirect('reminders')
    localize_form(form, request)
    return render(request, 'ledger/form.html', {'form': form, 'section': 'reminders',
        'form_title': 'Edit Reminder' if obj else 'Add Reminder', 'back_url': 'reminders', 'form_kind': 'reminder'})


@login_required
@require_POST
def reminder_toggle(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, owner=request.user)
    reminder.done = not reminder.done
    reminder.save(update_fields=['done'])
    return redirect('reminders')


@login_required
@require_POST
def reminder_delete(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, owner=request.user)
    reminder.delete()
    return redirect('reminders')


@login_required
def reports(request):
    qs = Expense.objects.filter(owner=request.user)
    totals = summarize(qs)
    grouped = list(qs.values('category').annotate(total=Sum('amount')).order_by('-total'))
    labels = dict(CATEGORY_CHOICES)
    for item in grouped:
        item['name'] = labels.get(item['category'], item['category'])
        item['percentage'] = round(float(item['total']) * 100 / float(totals['TOTAL'])) if totals['TOTAL'] else 0
    return render(request, 'ledger/reports.html', {'section': 'reports', 'totals': totals,
        'chart': chart_data(qs, 12), 'categories': grouped, 'fuel_breakdown': breakdown(qs.filter(category='FUEL')),
        'lifetime_records': qs.count()})


@login_required
def receipts(request):
    records = Expense.objects.filter(owner=request.user, receipt_photo__isnull=False).exclude(receipt_photo='').select_related('vehicle')[:100]
    return render(request, 'ledger/receipts.html', {'section': 'receipts', 'records': records})


@login_required
def downloads(request):
    return render(request, 'ledger/download.html', {'section': 'downloads'})


@login_required
def settings_page(request):
    if request.method == 'POST':
        name = request.POST.get('first_name', '').strip()[:80]
        email = request.POST.get('email', '').strip()[:254]
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email.')
        else:
            if request.user.__class__.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'This email is used by another account.')
            else:
                request.user.first_name = name
                request.user.email = email
                request.user.save(update_fields=['first_name','email'])
                messages.success(request, 'Profile updated.')
                return redirect('settings')
    return render(request, 'ledger/settings.html', {'section': 'settings'})


@login_required
def set_language(request, code):
    if code in ('bn','en'):
        request.session['app_language'] = code
    back = request.META.get('HTTP_REFERER', '')
    if url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(back)
    return redirect('dashboard')


def prevent_csv_formula(value):
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')):
        return "'" + value
    return value


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="AutoLedger_BD_Expenses.csv"'
    response.write('\ufeff')  # Excel supports Bangla with UTF-8 BOM.
    writer = csv.writer(response)
    writer.writerow(['Date', 'Vehicle', 'Plate', 'Category', 'Details', 'BDT Amount',
                     'Fuel Type', 'Quantity', 'Odometer KM', 'Location', 'Notes'])
    for row in Expense.objects.filter(owner=request.user).select_related('vehicle'):
        writer.writerow([row.date.isoformat(), prevent_csv_formula(row.vehicle.name),
                         prevent_csv_formula(row.vehicle.plate), row.get_category_display(),
                         prevent_csv_formula(row.description), row.amount, row.fuel_type,
                         row.quantity or '', row.odometer or '', prevent_csv_formula(row.location),
                         prevent_csv_formula(row.notes)])
    return response


def manifest(request):
    return JsonResponse({
        'name': 'AutoLedger BD — Car Expense Manager', 'short_name': 'AutoLedger BD',
        'description': 'Track fuel, maintenance, BRTA renewals and car costs in Bangladesh.',
        'lang': 'bn-BD', 'dir': 'auto', 'start_url': '/', 'scope': '/',
        'display': 'standalone', 'display_override': ['standalone', 'minimal-ui'],
        'background_color': '#f4f8f7', 'theme_color': '#006747',
        'icons': [
            {'src': '/static/img/icon-192.png?v=emblem1', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': '/static/img/icon-512.png?v=emblem1', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': '/static/img/icon-maskable-512.png?v=emblem1', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }, content_type='application/manifest+json')


def service_worker(request):
    # Cache only public static assets; no user-specific HTML/API/media is cached.
    from django.conf import settings
    js = (settings.BASE_DIR / 'static/js/service-worker.js').read_text(encoding='utf-8')
    response = HttpResponse(js, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-store'
    return response


@login_required
def vehicle_detail(request, pk):
    car = get_object_or_404(Vehicle, pk=pk, owner=request.user)
    activity = list(Expense.objects.filter(owner=request.user, vehicle=car)[:15])
    reminders = list(Reminder.objects.filter(owner=request.user, vehicle=car, done=False)[:6])
    total = Expense.objects.filter(owner=request.user, vehicle=car).aggregate(value=Sum('amount'))['value'] or 0
    today = timezone.localdate()
    month_total = Expense.objects.filter(owner=request.user, vehicle=car, date__month=today.month, date__year=today.year).aggregate(value=Sum('amount'))['value'] or 0
    return render(request, 'ledger/vehicle_detail.html', {
        'section':'vehicles', 'car':car, 'activity':activity, 'car_reminders':reminders,
        'car_total':total, 'month_total':month_total,
    })


@login_required
def drivers(request):
    rows = Driver.objects.filter(owner=request.user).select_related('assigned_vehicle', 'user')
    return render(request, 'ledger/drivers.html', {'section':'drivers','rows':rows})


@login_required
def driver_form(request, pk=None):
    obj = get_object_or_404(Driver, pk=pk, owner=request.user) if pk else None
    form = DriverForm(request.POST or None, instance=obj, owner=request.user)
    if request.method == 'POST' and form.is_valid():
        driver = form.save()
        messages.success(request, 'Driver profile and login account saved. Share the username and password with your driver securely.')
        return redirect('drivers')
    return render(request, 'ledger/form.html', {
        'section':'drivers', 'form':form,
        'form_title':'Edit Driver' if obj else 'Add Driver', 'back_url':'drivers', 'form_kind':'driver',
    })


@login_required
@require_POST
def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk, owner=request.user)
    if driver.user_id:
        driver.user.is_active = False
        driver.user.save(update_fields=['is_active'])
    driver.delete()
    messages.success(request, 'Driver deleted.')
    return redirect('drivers')
