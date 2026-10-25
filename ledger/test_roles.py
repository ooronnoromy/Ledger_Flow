from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from .models import Vehicle, Driver, Expense
from .access import DRIVER_GROUP

User = get_user_model()

class FleetRoleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username='fleetadmin', password='FleetOwner!4926')
        cls.other = User.objects.create_user(username='otheradmin', password='FleetOwner!4926')
        cls.car = Vehicle.objects.create(owner=cls.admin, name='Assigned Axio', plate='FLEET-01')
        cls.second = Vehicle.objects.create(owner=cls.admin, name='Private Corolla', plate='FLEET-02')
        cls.foreign = Vehicle.objects.create(owner=cls.other, name='Other fleet', plate='OTHER-01')
        cls.account = User.objects.create_user(username='driverlogin', password='DriverLogin!4926')
        cls.account.groups.add(Group.objects.create(name=DRIVER_GROUP))
        cls.driver = Driver.objects.create(owner=cls.admin, user=cls.account, name='Test Driver', phone='01712345678', assigned_vehicle=cls.car)

    def driver_data(self, **kwargs):
        data = {'name':'New Driver','phone':'01812345678','username':'newdriver',
                'password1':'DriverSecret!5824','password2':'DriverSecret!5824',
                'assigned_vehicle':self.car.pk,'account_active':'on'}
        data.update(kwargs)
        return data

    def test_admin_creates_driver_login_with_hashed_password(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('driver_add'), self.driver_data())
        self.assertRedirects(response, reverse('drivers'))
        driver = Driver.objects.get(name='New Driver')
        self.assertEqual(driver.owner, self.admin)
        self.assertEqual(driver.assigned_vehicle, self.car)
        self.assertTrue(driver.user.check_password('DriverSecret!5824'))
        self.assertNotEqual(driver.user.password, 'DriverSecret!5824')
        self.assertFalse(driver.user.is_staff)
        self.assertFalse(driver.user.is_superuser)
        client = Client()
        self.assertTrue(client.login(username='newdriver', password='DriverSecret!5824'))
        response = client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'ledger/driver_dashboard.html')
        self.assertContains(response, 'Assigned Axio')
        self.assertNotContains(response, 'Private Corolla')

    def test_other_fleet_assignment_and_duplicate_username_are_rejected(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('driver_add'), self.driver_data(assigned_vehicle=self.foreign.pk))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newdriver').exists())
        response = self.client.post(reverse('driver_add'), self.driver_data(username='DRIVERLOGIN'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Driver.objects.count(), 1)

    def test_weak_and_mismatched_passwords_do_not_create_accounts(self):
        self.client.force_login(self.admin)
        for passwords in [('12345678','12345678'),('DriverSecret!5824','wrong')]:
            self.client.post(reverse('driver_add'), self.driver_data(password1=passwords[0],password2=passwords[1]))
            self.assertFalse(User.objects.filter(username='newdriver').exists())

    def test_driver_cannot_access_admin_routes_even_by_direct_post(self):
        self.client.force_login(self.account)
        urls = [reverse('drivers'),reverse('driver_add'),reverse('driver_edit',args=[self.driver.pk]),
                reverse('vehicle_add'),reverse('vehicle_edit',args=[self.car.pk]),reverse('reports'),
                reverse('export_csv'),reverse('admin:index')]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code,403,url)
            self.assertEqual(self.client.post(url,{}).status_code,403,url)
        response = self.client.get(reverse('dashboard'))
        self.assertNotContains(response, 'data-admin-link')
        self.assertNotContains(response, 'href="/drivers/"')

    def test_driver_expense_is_assigned_to_fleet_and_tracks_submitter(self):
        self.client.force_login(self.account)
        data = {'vehicle':self.car.pk,'category':'TOLL','description':'Driver toll',
                'amount':'120','date':timezone.localdate().isoformat()}
        self.assertRedirects(self.client.post(reverse('expense_add'),data),reverse('dashboard'))
        record = Expense.objects.get(description='Driver toll')
        self.assertEqual(record.owner,self.admin)
        self.assertEqual(record.submitted_by,self.account)
        for car in [self.second,self.foreign]:
            data['vehicle'] = car.pk
            self.assertEqual(self.client.post(reverse('expense_add'),data).status_code,200)
        self.assertEqual(Expense.objects.filter(description='Driver toll').count(),1)
        self.assertEqual(self.client.get(reverse('expense_edit',args=[record.pk])).status_code,403)
        admin_client=Client();admin_client.force_login(self.admin)
        self.assertContains(admin_client.get(reverse('expenses')),'Driver toll')

    def test_admin_can_reassign_disable_and_reset_password(self):
        self.client.force_login(self.admin)
        url=reverse('driver_edit',args=[self.driver.pk])
        data=self.driver_data(username=self.account.username,name=self.driver.name,assigned_vehicle=self.second.pk,password1='',password2='')
        self.assertRedirects(self.client.post(url,data),reverse('drivers'))
        self.account.refresh_from_db()
        self.assertTrue(self.account.check_password('DriverLogin!4926'))
        driver_client=Client();driver_client.force_login(self.account)
        response=driver_client.get(reverse('dashboard'))
        self.assertContains(response,'Private Corolla')
        self.assertNotContains(response,'Assigned Axio')
        data.update(password1='ChangedDriver!5824',password2='ChangedDriver!5824')
        self.client.post(url,data)
        self.assertEqual(driver_client.get(reverse('dashboard')).status_code,302)
        self.assertTrue(driver_client.login(username=self.account.username,password='ChangedDriver!5824'))
        data.update(password1='',password2='');data.pop('account_active')
        self.client.post(url,data)
        self.assertEqual(driver_client.get(reverse('dashboard')).status_code,302)
        self.assertFalse(Client().login(username=self.account.username,password='ChangedDriver!5824'))

    def test_deleting_driver_disables_login_without_granting_admin_role(self):
        driver_client=Client();driver_client.force_login(self.account)
        self.client.force_login(self.admin)
        self.client.post(reverse('driver_delete',args=[self.driver.pk]))
        self.account.refresh_from_db()
        self.assertFalse(self.account.is_active)
        self.assertTrue(self.account.groups.filter(name=DRIVER_GROUP).exists())
        self.assertEqual(driver_client.get(reverse('dashboard')).status_code,302)

    def test_unassigned_driver_cannot_submit_expenses(self):
        self.driver.assigned_vehicle=None;self.driver.save()
        self.client.force_login(self.account)
        self.assertContains(self.client.get(reverse('dashboard')),'No car assigned')
        self.client.post(reverse('expense_add'),{'vehicle':self.car.pk,'category':'TOLL','description':'Not assigned','amount':'20','date':timezone.localdate().isoformat()})
        self.assertFalse(Expense.objects.filter(description='Not assigned').exists())

    def test_browser_session_cookie_and_five_minute_idle_expiry(self):
        self.assertEqual(settings.SESSION_IDLE_TIMEOUT,300)
        self.client.force_login(self.admin)
        response=self.client.get(reverse('dashboard'))
        cookie=response.cookies[settings.SESSION_COOKIE_NAME]
        self.assertEqual(cookie['expires'],'')
        self.assertEqual(cookie['max-age'],'')
        session=self.client.session
        session['last_activity']=timezone.now().timestamp()-301
        session.save()
        response=self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code,302)
        self.assertNotIn('_auth_user_id',self.client.session)

    def test_recent_activity_and_cache_control(self):
        self.client.force_login(self.admin)
        session=self.client.session;session['last_activity']=timezone.now().timestamp()-290;session.save()
        response=self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code,200)
        self.assertIn('no-store',response['Cache-Control'])
        self.assertGreater(self.client.session['last_activity'],timezone.now().timestamp()-5)

    def test_activity_heartbeat_requires_login_post_and_csrf(self):
        url = reverse('session_activity')
        self.assertEqual(self.client.post(url).status_code,302)
        client=Client(enforce_csrf_checks=True);client.force_login(self.account)
        self.assertEqual(client.get(url).status_code,405)
        self.assertEqual(client.post(url).status_code,403)
        client.get(reverse('dashboard'))
        response=client.post(url,{'csrfmiddlewaretoken':client.cookies['csrftoken'].value})
        self.assertEqual(response.status_code,204)
        session=client.session;session['last_activity']=timezone.now().timestamp()-301;session.save()
        self.assertEqual(client.post(url,{'csrfmiddlewaretoken':client.cookies['csrftoken'].value}).status_code,302)

    def test_self_registration_creates_fleet_admin_without_staff_privileges(self):
        data={'username':'registeredadmin','first_name':'Fleet Owner','email':'fleet@example.test',
              'password1':'OwnerPassword!8472','password2':'OwnerPassword!8472',
              'is_staff':'on','is_superuser':'on'}
        self.assertRedirects(self.client.post(reverse('register'),data),reverse('dashboard'))
        user=User.objects.get(username='registeredadmin')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.groups.filter(name=DRIVER_GROUP).exists())
        self.assertEqual(self.client.get(reverse('driver_add')).status_code,200)
