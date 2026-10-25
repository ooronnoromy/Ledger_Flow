import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import ExpenseNotification, PushSubscription
from .push import validate_subscription

@login_required
def inbox(request):
    notifications=ExpenseNotification.objects.filter(recipient=request.user).select_related('expense__vehicle','expense__submitted_by')[:100]
    return render(request,'ledger/notifications.html',{'section':'notifications','notifications':notifications})

@login_required
def push_config(request):
    return JsonResponse({'publicKey':settings.WEBPUSH_PUBLIC_KEY,'ready':bool(settings.WEBPUSH_PUBLIC_KEY)})

@login_required
@require_POST
@transaction.atomic
def subscribe(request):
    if len(request.body)>4096:
        return JsonResponse({'error':'Subscription is too large.'},status=400)
    try:
        endpoint,keys=validate_subscription(json.loads(request.body))
    except (ValueError,TypeError):
        return JsonResponse({'error':'Invalid subscription.'},status=400)
    existing=PushSubscription.objects.select_for_update().filter(endpoint=endpoint).first()
    if existing:
        if existing.keys!=keys:
            return JsonResponse({'error':'This device subscription cannot be changed.'},status=409)
        if existing.user_id!=request.user.pk:
            existing.deliveries.filter(sent_at__isnull=True).delete()
        existing.user=request.user;existing.save(update_fields=['user'])
    else:
        if request.user.push_subscriptions.count()>=10:
            return JsonResponse({'error':'Device limit reached. Disable notifications on another device first.'},status=400)
        PushSubscription.objects.create(user=request.user,endpoint=endpoint,keys=keys)
    return JsonResponse({'enabled':True})

@login_required
@require_POST
def unsubscribe(request):
    try:
        if len(request.body)>4096: raise ValueError()
        endpoint=json.loads(request.body).get('endpoint')
    except (ValueError,AttributeError):
        return JsonResponse({'error':'Invalid request.'},status=400)
    PushSubscription.objects.filter(user=request.user,endpoint=endpoint).delete()
    return JsonResponse({'enabled':False})

@login_required
@require_POST
def open_notification(request,pk):
    notification=get_object_or_404(ExpenseNotification,pk=pk,recipient=request.user)
    if not notification.read_at:
        notification.read_at=timezone.now();notification.save(update_fields=['read_at'])
    expense=notification.expense
    if not expense:return redirect('notifications')
    if expense.owner_id==request.user.pk:return redirect('expense_edit',pk=expense.pk)
    if request.user.is_superuser:return redirect('admin:ledger_expense_change',expense.pk)
    return redirect('notifications')

@login_required
def notification_landing(request,pk):
    # Notification taps use GET; the inbox's CSRF-protected button marks it read.
    notification=get_object_or_404(ExpenseNotification.objects.select_related('expense__vehicle'),pk=pk,recipient=request.user)
    return render(request,'ledger/notifications.html',{'section':'notifications','notifications':[notification]})
