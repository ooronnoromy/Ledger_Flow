import base64
import json
from types import SimpleNamespace
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from pywebpush import WebPushException
from .models import Vehicle, Expense, Driver, ExpenseNotification, PushSubscription, PushDelivery
from .push import deliver
from .access import DRIVER_GROUP

User=get_user_model()

def device(endpoint='https://fcm.googleapis.com/fcm/send/test-device'):
    public=ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
    encode=lambda value:base64.urlsafe_b64encode(value).decode().rstrip('=')
    return {'endpoint':endpoint,'keys':{'p256dh':encode(public),'auth':encode(b'0123456789abcdef')}}

class NotificationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin=User.objects.create_user('owner',password='OwnerSecret!4286')
        cls.other=User.objects.create_user('other',password='OwnerSecret!4286')
        cls.superuser=User.objects.create_superuser('superuser','owner@example.test','OwnerSecret!4286')
        cls.car=Vehicle.objects.create(owner=cls.admin,name='Axio',plate='NOTIFY-01')

    def record(self):
        return Expense.objects.create(owner=self.admin,vehicle=self.car,category='TOLL',description='Toll expense',amount='150',submitted_by=self.admin)

    def test_new_expense_notifies_owner_and_superuser_only_once(self):
        expense=self.record()
        self.assertEqual(set(expense.notifications.values_list('recipient_id',flat=True)),{self.admin.pk,self.superuser.pk})
        expense.description='Edited expense';expense.save()
        self.assertEqual(expense.notifications.count(),2)
        owncar=Vehicle.objects.create(owner=self.superuser,name='Superuser car',plate='NOTIFY-02')
        ownexpense=Expense.objects.create(owner=self.superuser,vehicle=owncar,category='TOLL',description='Own expense',amount=20)
        self.assertEqual(ownexpense.notifications.count(),1)

    def test_failed_transaction_leaves_no_notification_or_push(self):
        payload=device();PushSubscription.objects.create(user=self.admin,endpoint=payload['endpoint'],keys=payload['keys'])
        with patch('ledger.push.webpush') as send:
            try:
                with transaction.atomic():
                    self.record()
                    raise ValueError('Rollback')
            except ValueError:pass
        self.assertFalse(ExpenseNotification.objects.exists())
        self.assertFalse(PushDelivery.objects.exists())
        send.assert_not_called()

    def test_notification_privacy_and_read_tracking(self):
        expense=self.record();notification=expense.notifications.get(recipient=self.admin)
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(reverse('notifications')),'Toll expense')
        self.assertEqual(self.client.get(reverse('notification_landing',args=[notification.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('notification_open',args=[notification.pk])).status_code,404)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse('notifications')),'Toll expense')
        self.assertEqual(self.client.get(reverse('notification_open',args=[notification.pk])).status_code,405)
        self.assertRedirects(self.client.post(reverse('notification_open',args=[notification.pk])),reverse('expense_edit',args=[expense.pk]))
        notification.refresh_from_db();self.assertIsNotNone(notification.read_at)
        super_notification=expense.notifications.get(recipient=self.superuser)
        self.client.force_login(self.superuser)
        self.assertRedirects(self.client.post(reverse('notification_open',args=[super_notification.pk])),reverse('admin:ledger_expense_change',args=[expense.pk]))

    def test_device_registration_validation_and_csrf(self):
        url=reverse('push_subscribe');payload=device()
        self.assertEqual(self.client.post(url,json.dumps(payload),content_type='application/json').status_code,302)
        client=Client(enforce_csrf_checks=True);client.force_login(self.admin)
        self.assertEqual(client.post(url,json.dumps(payload),content_type='application/json').status_code,403)
        client.get(reverse('settings'))
        response=client.post(url,json.dumps(payload),content_type='application/json',HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code,200)
        self.assertEqual(PushSubscription.objects.get().user,self.admin)

    def test_arbitrary_endpoints_and_invalid_keys_rejected(self):
        self.client.force_login(self.admin)
        for endpoint in ['https://127.0.0.1/','http://fcm.googleapis.com/a','https://fcm.googleapis.com.attacker.test/a','https://fcm.googleapis.com:8443/a','https://user@fcm.googleapis.com/a']:
            response=self.client.post(reverse('push_subscribe'),json.dumps(device(endpoint)),content_type='application/json')
            self.assertEqual(response.status_code,400)
        payload=device();payload['keys']['auth']='invalid'
        self.assertEqual(self.client.post(reverse('push_subscribe'),json.dumps(payload),content_type='application/json').status_code,400)
        self.assertFalse(PushSubscription.objects.exists())

    def test_device_cannot_be_hijacked_and_unsubscribe_is_owner_scoped(self):
        payload=device();subscription=PushSubscription.objects.create(user=self.admin,endpoint=payload['endpoint'],keys=payload['keys'])
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(reverse('push_subscribe'),json.dumps(device()),content_type='application/json').status_code,409)
        self.client.post(reverse('push_unsubscribe'),json.dumps({'endpoint':payload['endpoint']}),content_type='application/json')
        self.assertTrue(PushSubscription.objects.filter(pk=subscription.pk).exists())
        self.client.force_login(self.admin)
        self.client.post(reverse('push_unsubscribe'),json.dumps({'endpoint':payload['endpoint']}),content_type='application/json')
        self.assertFalse(PushSubscription.objects.exists())

    @override_settings(WEBPUSH_PUBLIC_KEY='test-public',WEBPUSH_PRIVATE_KEY='test-private',WEBPUSH_SUBJECT='mailto:test@example.test')
    def test_push_after_commit_is_generic_and_sent_once(self):
        payload=device();PushSubscription.objects.create(user=self.admin,endpoint=payload['endpoint'],keys=payload['keys'])
        with patch('ledger.push.webpush') as send:
            with self.captureOnCommitCallbacks(execute=True):
                expense=self.record()
            send.assert_called_once()
            content=json.loads(send.call_args.kwargs['data'])
            self.assertNotIn('150',content['body'])
            self.assertNotIn(expense.description,content['body'])
            self.assertTrue(content['url'].startswith('/notifications/'))
            delivery=PushDelivery.objects.get();self.assertIsNotNone(delivery.sent_at)
            deliver(delivery.pk);send.assert_called_once()

    @override_settings(WEBPUSH_PUBLIC_KEY='test-public',WEBPUSH_PRIVATE_KEY='test-private')
    def test_delivery_failure_does_not_lose_expense_and_can_retry(self):
        payload=device();PushSubscription.objects.create(user=self.admin,endpoint=payload['endpoint'],keys=payload['keys'])
        with patch('ledger.push.webpush',side_effect=RuntimeError('Unavailable')):
            with self.captureOnCommitCallbacks(execute=True):expense=self.record()
        self.assertTrue(Expense.objects.filter(pk=expense.pk).exists())
        delivery=PushDelivery.objects.get();self.assertIsNone(delivery.sent_at)
        with patch('ledger.push.webpush') as send:self.assertTrue(deliver(delivery.pk))
        send.assert_called_once()

    @override_settings(WEBPUSH_PUBLIC_KEY='test-public',WEBPUSH_PRIVATE_KEY='test-private')
    def test_expired_device_removed(self):
        payload=device();PushSubscription.objects.create(user=self.admin,endpoint=payload['endpoint'],keys=payload['keys'])
        error=WebPushException('Expired',response=SimpleNamespace(status_code=410))
        with patch('ledger.push.webpush',side_effect=error):
            with self.captureOnCommitCallbacks(execute=True):self.record()
        self.assertFalse(PushSubscription.objects.exists())

    def test_driver_cannot_subscribe_or_access_admin_notifications(self):
        driver=User.objects.create_user('notify-driver',password='DriverSecret!4286')
        driver.groups.add(Group.objects.get_or_create(name=DRIVER_GROUP)[0])
        Driver.objects.create(owner=self.admin,user=driver,name='Driver',phone='01712345678',assigned_vehicle=self.car)
        self.client.force_login(driver)
        self.assertEqual(self.client.get(reverse('notifications')).status_code,403)
        self.assertEqual(self.client.get(reverse('push_config')).status_code,403)
        self.assertEqual(self.client.post(reverse('push_subscribe'),json.dumps(device()),content_type='application/json').status_code,403)

    @override_settings(WEBPUSH_PUBLIC_KEY='only-public-key',WEBPUSH_PRIVATE_KEY='never-expose-this-private-key')
    def test_config_exposes_only_public_key_and_requires_login(self):
        self.assertEqual(self.client.get(reverse('push_config')).status_code,302)
        self.client.force_login(self.admin)
        response=self.client.get(reverse('push_config'))
        self.assertEqual(response.json(),{'publicKey':'only-public-key','ready':True})
        self.assertNotContains(response,'never-expose')

    def test_same_browser_device_can_switch_accounts_without_old_pending_alerts(self):
        payload=device();subscription=PushSubscription.objects.create(user=self.admin,endpoint=payload['endpoint'],keys=payload['keys'])
        self.record()
        self.assertTrue(PushDelivery.objects.filter(subscription=subscription).exists())
        self.client.force_login(self.other)
        response=self.client.post(reverse('push_subscribe'),json.dumps(payload),content_type='application/json')
        self.assertEqual(response.status_code,200)
        subscription.refresh_from_db();self.assertEqual(subscription.user,self.other)
        self.assertFalse(PushDelivery.objects.filter(subscription=subscription,sent_at__isnull=True).exists())
