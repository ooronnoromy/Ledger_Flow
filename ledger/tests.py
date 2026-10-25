from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Vehicle, Expense, Reminder, Driver


class AppTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.a = User.objects.create_user(username='testdriver1',password='SafePass1234!')
        self.b = User.objects.create_user(username='testdriver2',password='SafePass1234!')
        self.car_a = Vehicle.objects.create(owner=self.a,name='Toyota Axio',plate='DEMO-A',fuel_type='OCTANE')
        self.car_b = Vehicle.objects.create(owner=self.b,name='Toyota Corolla',plate='DEMO-B',fuel_type='CNG')
        self.expense_b = Expense.objects.create(owner=self.b,vehicle=self.car_b,category='FUEL',
            description='Private refill',amount=Decimal('1234.50'),fuel_type='CNG',quantity=Decimal('12.0'))

    def test_login_required(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code,302)

    def test_dashboard_for_own_account(self):
        self.client.force_login(self.a)
        response=self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'AutoLedger')
        self.assertNotContains(response,'Private refill')

    def test_user_cannot_edit_someone_elses_expense(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('expense_edit',args=[self.expense_b.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('expense_delete',args=[self.expense_b.pk])).status_code,404)

    def test_post_only_delete(self):
        self.client.force_login(self.b)
        self.assertEqual(self.client.get(reverse('expense_delete',args=[self.expense_b.pk])).status_code,405)

    def test_cross_account_vehicle_submission_blocked(self):
        self.client.force_login(self.a)
        response=self.client.post(reverse('expense_add'),{
            'vehicle':self.car_b.pk,'category':'FUEL','description':'Hacked',
            'amount':'700','date':timezone.localdate().isoformat(),
            'fuel_type':'CNG','quantity':'10',
        })
        self.assertEqual(response.status_code,200)
        self.assertFalse(Expense.objects.filter(owner=self.a,description='Hacked').exists())

    def test_reminder_toggle(self):
        reminder=Reminder.objects.create(owner=self.a,vehicle=self.car_a,title='BRTA Fitness',
            due_date=timezone.localdate()+timedelta(days=10))
        self.client.force_login(self.a)
        self.client.post(reverse('reminder_toggle',args=[reminder.pk]))
        reminder.refresh_from_db()
        self.assertTrue(reminder.done)

    def test_export_csv_is_private(self):
        self.client.force_login(self.a)
        response=self.client.get(reverse('export_csv'))
        self.assertEqual(response.status_code,200)
        self.assertNotIn('Private refill',response.content.decode('utf-8'))

    def test_manifest_public(self):
        r=self.client.get(reverse('manifest'))
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['short_name'],'AutoLedger BD')

    def test_account_signout_requires_post_and_clears_session(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)

    def test_admin_shortcut_visible_only_to_superuser(self):
        self.client.force_login(self.a)
        self.assertNotContains(self.client.get(reverse('dashboard')), 'data-admin-link')
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 302)
        self.a.is_staff = True
        self.a.save(update_fields=['is_staff'])
        self.assertNotContains(self.client.get(reverse('dashboard')), 'data-admin-link')
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 302)
        self.a.is_superuser = True
        self.a.save(update_fields=['is_superuser'])
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'data-admin-link')
        self.assertContains(response, f'href="{reverse("admin:index")}"')
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 200)

    def test_signout_requires_csrf_token(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.a)
        self.assertEqual(client.post(reverse('logout')).status_code, 403)
        client.get(reverse('dashboard'))
        token = client.cookies['csrftoken'].value
        response = client.post(reverse('logout'), {'csrfmiddlewaretoken':token})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', client.session)

    def test_password_change_validates_old_password_and_keeps_current_session(self):
        self.client.force_login(self.a)
        url = reverse('password_change')
        self.assertEqual(self.client.get(url).status_code, 200)
        password = 'NewStrongPass-4268!'
        response = self.client.post(url, {'old_password':'wrong', 'new_password1':password, 'new_password2':password})
        self.assertEqual(response.status_code, 200)
        self.a.refresh_from_db()
        self.assertTrue(self.a.check_password('SafePass1234!'))
        response = self.client.post(url, {'old_password':'SafePass1234!', 'new_password1':password, 'new_password2':password})
        self.assertRedirects(response, reverse('password_change_done'))
        self.a.refresh_from_db()
        self.assertTrue(self.a.check_password(password))
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)

    def test_password_change_requires_login(self):
        self.assertEqual(self.client.get(reverse('password_change')).status_code, 302)

    def test_trip_costs_filter(self):
        self.client.force_login(self.a)
        Expense.objects.create(owner=self.a, vehicle=self.car_a, category='TRIP',
                               description='Dhaka to Gazipur', amount=Decimal('950'))
        r = self.client.get(reverse('expenses') + '?category=TRIP')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Dhaka to Gazipur')
        self.assertNotContains(r, 'Private refill')

    def test_vehicle_detail_owner_scoped(self):
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('vehicle_detail', args=[self.car_a.pk])).status_code,200)
        self.assertEqual(self.client.get(reverse('vehicle_detail', args=[self.car_b.pk])).status_code,404)

    def test_driver_security(self):
        other = Driver.objects.create(owner=self.b, name='Another Driver', phone='01712345678')
        self.client.force_login(self.a)
        self.assertEqual(self.client.get(reverse('driver_edit', args=[other.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('driver_delete', args=[other.pk])).status_code,404)
        self.assertEqual(self.client.get(reverse('drivers')).status_code,200)
        bad = self.client.post(reverse('driver_add'), {
            'name':'Test Driver','phone':'01712345678','assigned_vehicle':self.car_b.pk,
        })
        self.assertEqual(bad.status_code,200)
        self.assertFalse(Driver.objects.filter(owner=self.a, name='Test Driver').exists())

    def test_install_assets_public(self):
        self.assertEqual(self.client.get(reverse('service_worker')).status_code,200)
        self.assertIn('/static/css/reference.css', self.client.get(reverse('service_worker')).content.decode())
