"""Render representative role screens without creating database users or sessions."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings
from ledger.forms import DriverForm
from ledger.models import Driver,Vehicle,Expense,ExpenseNotification
from django.utils import timezone

admin=User(pk=-1,username='fleetadmin',first_name='Tanvir Ahmed')
driver_user=User(pk=-2,username='driverlogin',first_name='Rahim Uddin')
driver_user._is_fleet_driver=True
admin._is_fleet_driver=False
car=Vehicle(pk=-1,owner=admin,name='Toyota Axio',plate='ঢাকা মেট্রো-গ-১২-৩৪৫৬',odometer=68250)
driver=Driver(pk=-1,user=driver_user,owner=admin,name='Rahim Uddin',phone='01712345678',assigned_vehicle=car)
expense=Expense(pk=9999,owner=admin,vehicle=car,description='Octane refill',amount=3000,submitted_by=driver_user)
notification=ExpenseNotification(pk=9999,recipient=admin,expense=expense,created_at=timezone.now())
factory=RequestFactory()
with override_settings(STORAGES={'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}}):
    for filename,user,template,context in [
        ('preview-driver.html',driver_user,'ledger/driver_dashboard.html',{'section':'dashboard','driver':driver,'car':car,'records':[],'driver_total':0}),
        ('preview-driver-form.html',admin,'ledger/form.html',{'section':'drivers','form':DriverForm(owner=None),'form_title':'Add Driver','back_url':'drivers','form_kind':'driver'}),
        ('preview-notifications.html',admin,'ledger/notifications.html',{'section':'notifications','notifications':[notification],'notification_unread':1}),
        ('preview-push-settings.html',admin,'ledger/settings.html',{'section':'settings'}),
    ]:
        request=factory.get('/');request.user=user;request.session={'app_language':'en'}
        html=render_to_string(template,context,request=request)
        html=html.replace('="/static/','="static/').replace("=' /static/","='static/")
        # These local visual fixtures have no live login session or HTTP endpoints.
        html=html.replace('data-session-timeout="300"','data-session-timeout="0"')
        (ROOT/filename).write_text(html,encoding='utf-8')
