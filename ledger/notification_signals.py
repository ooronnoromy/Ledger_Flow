from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Expense, ExpenseNotification, PushDelivery, PushSubscription
from .push import deliver

@receiver(post_save, sender=Expense, dispatch_uid='expense_created_notifications')
def expense_created(sender, instance, created, raw=False, **kwargs):
    if not created or raw:
        return
    recipients = {instance.owner_id}
    if settings.PUSH_NOTIFY_SUPERUSERS:
        recipients.update(get_user_model().objects.filter(is_superuser=True,is_active=True).values_list('pk',flat=True))
    for user_id in recipients:
        notification = ExpenseNotification.objects.create(recipient_id=user_id,expense=instance)
        for subscription in PushSubscription.objects.filter(user_id=user_id,user__is_active=True):
            delivery = PushDelivery.objects.create(notification=notification,subscription=subscription)
            transaction.on_commit(lambda pk=delivery.pk: deliver(pk), robust=True)
