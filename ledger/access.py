from .models import Driver, Vehicle

DRIVER_GROUP = 'AutoLedger Drivers'

def is_driver(user):
    if not user.is_authenticated or user.is_superuser:
        return False
    if not hasattr(user, '_is_fleet_driver'):
        user._is_fleet_driver = (Driver.objects.filter(user=user).exists() or user.groups.filter(name=DRIVER_GROUP).exists())
    return user._is_fleet_driver

def available_vehicles(user):
    if is_driver(user):
        return Vehicle.objects.filter(assigned_drivers__user=user, owner__is_active=True)
    return Vehicle.objects.filter(owner=user)
