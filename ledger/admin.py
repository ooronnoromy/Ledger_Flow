from django.contrib import admin
from .models import Vehicle, Expense, Reminder, Driver

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name','plate','owner','fuel_type','odometer')
    search_fields = ('name','plate','owner__username')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date','description','category','amount','vehicle','owner','submitted_by')
    list_filter = ('category','date')
    search_fields = ('description','vehicle__plate')

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('title','vehicle','due_date','due_odometer','done')
    list_filter = ('done',)


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name','phone','assigned_vehicle','owner','user')
    search_fields = ('name','phone','owner__username')
