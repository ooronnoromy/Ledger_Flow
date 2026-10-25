"""Populate clearly fictional expenses for one existing user, idempotently."""
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from ledger.models import Vehicle, Expense, Reminder


class Command(BaseCommand):
    help = 'Create sample Bangladesh car expense data for a named existing user. Uses fictional plates.'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(username=options['username'])
        except User.DoesNotExist:
            raise CommandError('User does not exist. Create one via /register/ or createsuperuser.')
        if Vehicle.objects.filter(owner=user, plate='DEMO-DHAKA-001').exists():
            self.stdout.write('Demo data already exists for this user. No duplicates created.')
            return
        car = Vehicle.objects.create(owner=user, name='Toyota Axio',brand='Toyota',
            model_year=2018,plate='DEMO-DHAKA-001',fuel_type='OCTANE',odometer=68250,color='Silver')
        car2 = Vehicle.objects.create(owner=user,name='Toyota Corolla',brand='Toyota',
            model_year=2020,plate='DEMO-DHAKA-002',fuel_type='CNG',odometer=38120,color='White')
        now = timezone.localdate()
        records = [
            (0,car,'FUEL','Octane Refill', '3840.00','OCTANE','30.0','Bashundhara R/A, Dhaka'),
            (1,car2,'FUEL','CNG Refill', '850.00','CNG','12.0','Uttara CNG Station'),
            (2,car,'MAINTENANCE','Engine Oil (Mobil 1)', '5500.00','','','Gulshan, Dhaka'),
            (3,car2,'TOLL','Dhaka–Chattogram Highway Toll', '250.00','','','Meghna Bridge'),
            (5,car,'WASH','Car Wash', '450.00','','','Mirpur DOHS'),
            (7,car,'FUEL','Octane Refill', '4100.00','OCTANE','31.5','Dhanmondi, Dhaka'),
            (9,car2,'MAINTENANCE','Brake Pads Replacement', '8200.00','','','Uttara Service Center'),
            (12,car,'FUEL','Octane Refill', '3500.00','OCTANE','27.5','Banani, Dhaka'),
            (16,car2,'INSURANCE','Car Insurance Renewal', '6500.00','','','Dhaka'),
            (20,car,'FUEL','Octane Refill', '4200.00','OCTANE','33.0','Gulshan, Dhaka'),
            (31,car2,'TAX','Tax Token Renewal', '5000.00','','','BRTA'),
            (46,car,'MAINTENANCE','Air Filter Replacement', '1550.00','','','Dhaka'),
            (66,car2,'FUEL','CNG Refill', '900.00','CNG','14.0','Mohakhali, Dhaka'),
            (89,car,'MAINTENANCE','Wheel Alignment', '1800.00','','','Tejgaon'),
            (125,car,'FUEL','Octane Refill', '3670.00','OCTANE','29.5','Dhanmondi'),
            (153,car2,'FUEL','CNG Refill', '810.00','CNG','12.8','Uttara'),
        ]
        for (days,vehicle,category,description,amount,ft,quantity,loc) in records:
            Expense.objects.create(owner=user,vehicle=vehicle,category=category,
                description=description,amount=Decimal(amount),date=now-timedelta(days=days),
                location=loc,fuel_type=ft,quantity=Decimal(quantity) if quantity else None)
        for vehicle,title,delta,due_km in [
            (car,'BRTA Fitness Renewal',40,None),
            (car,'Engine Oil Change',None,69500),
            (car2,'Tax Token Renewal',75,None),
            (car2,'Brake Pad Check',None,42000),
            (car,'Insurance Renewal',95,None),
        ]:
            Reminder.objects.create(owner=user,vehicle=vehicle,title=title,
                due_date=now+timedelta(days=delta) if delta is not None else None,due_odometer=due_km)
        self.stdout.write(self.style.SUCCESS('Demo data created for user ' + user.username))
