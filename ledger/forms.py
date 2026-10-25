from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Vehicle, Expense, Reminder, Driver
from .access import available_vehicles, DRIVER_GROUP
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group
from django.db import transaction


def check_image(value):
    if not value or not hasattr(value, 'content_type'):
        return
    if value.size > 8 * 1024 * 1024:
        raise ValidationError('Maximum photo size: 8 MB.')
    if value.content_type not in ('image/jpeg', 'image/png', 'image/webp'):
        raise ValidationError('Upload a JPG, PNG, or WebP image.')


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=80, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('This email is already registered.')
        return email


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'brand', 'model_year', 'plate', 'fuel_type', 'odometer', 'color', 'photo']
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Toyota Axio'}),
                   'plate': forms.TextInput(attrs={'placeholder': 'ঢাকা মেট্রো-গ-১২-৩৪৫৬'})}

    def clean_photo(self):
        value = self.cleaned_data.get('photo')
        check_image(value)
        return value


class ExpenseForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Expense
        fields = ['vehicle', 'category', 'description', 'amount', 'date', 'location',
                  'fuel_type', 'quantity', 'odometer', 'receipt_photo', 'meter_photo', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3}),
                   'location': forms.TextInput(attrs={'placeholder': 'Dhanmondi, Dhaka'}),
                   'amount': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
                   'quantity': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
                   'description': forms.TextInput(attrs={'placeholder': 'Octane refill / Engine oil change'})}

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = available_vehicles(owner) if owner else Vehicle.objects.none()
        for field in ('receipt_photo', 'meter_photo'):
            self.fields[field].widget.attrs['accept'] = 'image/jpeg,image/png,image/webp'

    def clean_receipt_photo(self):
        f = self.cleaned_data.get('receipt_photo')
        check_image(f)
        return f

    def clean_meter_photo(self):
        f = self.cleaned_data.get('meter_photo')
        check_image(f)
        return f

    def clean(self):
        data = super().clean()
        if data.get('category') == 'FUEL':
            if not data.get('fuel_type'):
                self.add_error('fuel_type', 'Select fuel type for refueling.')
            if not data.get('quantity'):
                self.add_error('quantity', 'Enter fuel quantity (litres or CNG units).')
        return data


class ReminderForm(forms.ModelForm):
    due_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Reminder
        fields = ['vehicle', 'title', 'due_date', 'due_odometer', 'notes']
        widgets = {'title': forms.TextInput(attrs={'placeholder': 'BRTA Fitness Renewal'})}

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=owner) if owner else Vehicle.objects.none()

    def clean(self):
        data = super().clean()
        if not data.get('due_date') and not data.get('due_odometer'):
            raise ValidationError('Enter at least a due date or target odometer.')
        return data


class DriverForm(forms.ModelForm):
    username = forms.CharField(max_length=150, validators=User._meta.get_field('username').validators, help_text='The driver will use this username to sign in.')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False, help_text='Set a password for a new driver. Leave blank when editing to keep the current password.')
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput, required=False)
    account_active = forms.BooleanField(label='Allow this driver to log in', required=False, initial=True)
    class Meta:
        model = Driver
        fields = ['name', 'phone', 'license_number', 'assigned_vehicle']
        widgets = {'phone': forms.TextInput(attrs={'placeholder': '01XXXXXXXXX', 'inputmode': 'tel'}),
                   'license_number': forms.TextInput(attrs={'placeholder': 'BRTA License Number'})}

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_vehicle'].queryset = Vehicle.objects.filter(owner=owner) if owner else Vehicle.objects.none()
        self.owner = owner
        if self.instance.pk and self.instance.user_id:
            self.initial['username'] = self.instance.user.username
            self.initial['account_active'] = self.instance.user.is_active
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        existing = User.objects.filter(username__iexact=username)
        if self.instance.pk and self.instance.user_id:
            existing = existing.exclude(pk=self.instance.user_id)
        if existing.exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean(self):
        data = super().clean()
        password = data.get('password1')
        if password != data.get('password2'):
            self.add_error('password2', 'Passwords do not match.')
        if password:
            user = User(username=data.get('username', ''), first_name=data.get('name', ''))
            try:
                validate_password(password, user=user)
            except ValidationError as errors:
                self.add_error('password1', errors)
        return data

    @transaction.atomic
    def save(self, commit=True):
        if not commit:
            raise ValueError('Driver accounts must be saved atomically with their profile.')
        driver = super().save(commit=False)
        user = driver.user if driver.user_id else User()
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['name'][:150]
        user.is_active = self.cleaned_data['account_active']
        user.is_staff = False
        user.is_superuser = False
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        user.save()
        group, _ = Group.objects.get_or_create(name=DRIVER_GROUP)
        user.groups.add(group)
        driver.user = user
        driver.owner = self.owner
        driver.save()
        return driver

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        import re
        if not re.fullmatch(r'(?:\+?88)?01[3-9][0-9]{8}', phone):
            raise ValidationError('Enter a valid Bangladeshi number such as 01712345678.')
        return phone
