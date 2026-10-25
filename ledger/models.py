from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

FUEL_CHOICES = [
    ('OCTANE', 'Octane / অকটেন'), ('PETROL', 'Petrol / পেট্রোল'),
    ('DIESEL', 'Diesel / ডিজেল'), ('CNG', 'CNG / সিএনজি'),
    ('LPG', 'LPG / এলপিজি'), ('ELECTRIC', 'Electric / বিদ্যুৎ'),
]
CATEGORY_CHOICES = [
    ('FUEL', 'Fuel / জ্বালানি'), ('MAINTENANCE', 'Maintenance / মেইনটেন্যান্স'),
    ('TRIP', 'Trip Cost / যাতায়াত'), ('TOLL', 'Toll / টোল'), ('PARKING', 'Parking / পার্কিং'),
    ('WASH', 'Car Wash / কার ওয়াশ'), ('TAX', 'Tax Token / ট্যাক্স টোকেন'),
    ('FITNESS', 'BRTA Fitness / ফিটনেস'), ('INSURANCE', 'Insurance / ইন্স্যুরেন্স'),
    ('OTHER', 'Other / অন্যান্য'),
]


class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=120)
    brand = models.CharField(max_length=80, blank=True)
    model_year = models.PositiveIntegerField(default=2020)
    plate = models.CharField(max_length=80)
    fuel_type = models.CharField(max_length=16, choices=FUEL_CHOICES, default='OCTANE')
    odometer = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=40, default='Silver', blank=True)
    photo = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.plate})'


class Expense(models.Model):
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_expenses')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField(default=timezone.localdate)
    location = models.CharField(max_length=180, blank=True)
    fuel_type = models.CharField(max_length=16, choices=FUEL_CHOICES, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0.01)])
    odometer = models.PositiveIntegerField(blank=True, null=True)
    receipt_photo = models.ImageField(upload_to='receipts/', blank=True, null=True)
    meter_photo = models.ImageField(upload_to='meters/', blank=True, null=True)
    notes = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'{self.description} - ৳{self.amount}'


class Reminder(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=140)
    due_date = models.DateField(blank=True, null=True)
    due_odometer = models.PositiveIntegerField(blank=True, null=True)
    done = models.BooleanField(default=False)
    notes = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['done', 'due_date', 'id']

    def __str__(self):
        return self.title


class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_profile')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='drivers')
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=80, blank=True)
    assigned_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, blank=True, null=True, related_name='assigned_drivers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class ExpenseNotification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_notifications')
    expense = models.ForeignKey(Expense, on_delete=models.SET_NULL, null=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-pk']


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=2048, unique=True)
    keys = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class PushDelivery(models.Model):
    notification = models.ForeignKey(ExpenseNotification, on_delete=models.CASCADE, related_name='deliveries')
    subscription = models.ForeignKey(PushSubscription, on_delete=models.CASCADE, related_name='deliveries')
    sent_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['notification','subscription'], name='unique_notification_device')]
