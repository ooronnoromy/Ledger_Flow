from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.http import require_safe

from .access import available_vehicles
from .models import Expense, Vehicle


@require_safe
def healthcheck(request):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        cursor.fetchone()
    return HttpResponse('ok', content_type='text/plain')


@login_required
@require_safe
def private_media(request, path):
    """Serve uploaded images only to accounts allowed to see their records."""
    vehicles = Vehicle.objects.all() if request.user.is_superuser else available_vehicles(request.user)
    vehicle = vehicles.filter(photo=path).first()
    field = vehicle.photo if vehicle else None
    if field is None:
        expenses = Expense.objects.all() if request.user.is_superuser else Expense.objects.filter(owner=request.user)
        expense = expenses.filter(Q(receipt_photo=path) | Q(meter_photo=path)).first()
        if expense:
            field = expense.receipt_photo if expense.receipt_photo.name == path else expense.meter_photo
    if not field:
        raise Http404
    try:
        response = FileResponse(field.open('rb'))
    except (FileNotFoundError, ValueError):
        raise Http404
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
