from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Vehicle', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name',models.CharField(max_length=120)),
            ('brand',models.CharField(blank=True,max_length=80)),
            ('model_year',models.PositiveIntegerField(default=2020)),
            ('plate',models.CharField(max_length=80)),
            ('fuel_type',models.CharField(choices=[('OCTANE','Octane / অকটেন'),('PETROL','Petrol / পেট্রোল'),('DIESEL','Diesel / ডিজেল'),('CNG','CNG / সিএনজি'),('LPG','LPG / এলপিজি'),('ELECTRIC','Electric / বিদ্যুৎ')],default='OCTANE',max_length=16)),
            ('odometer',models.PositiveIntegerField(default=0)),
            ('color',models.CharField(blank=True,default='Silver',max_length=40)),
            ('photo',models.ImageField(blank=True,null=True,upload_to='vehicles/')),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='vehicles',to=settings.AUTH_USER_MODEL)),
        ], options={'ordering':['-created_at']}),
        migrations.CreateModel(name='Expense', fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('category',models.CharField(choices=[('FUEL','Fuel / জ্বালানি'),('MAINTENANCE','Maintenance / মেইনটেন্যান্স'),('TOLL','Toll / টোল'),('PARKING','Parking / পার্কিং'),('WASH','Car Wash / কার ওয়াশ'),('TAX','Tax Token / ট্যাক্স টোকেন'),('FITNESS','BRTA Fitness / ফিটনেস'),('INSURANCE','Insurance / ইন্স্যুরেন্স'),('OTHER','Other / অন্যান্য')],max_length=20)),
            ('description',models.CharField(max_length=180)),
            ('amount',models.DecimalField(decimal_places=2,max_digits=12,validators=[django.core.validators.MinValueValidator(0.01)])),
            ('date',models.DateField(default=django.utils.timezone.localdate)),
            ('location',models.CharField(blank=True,max_length=180)),
            ('fuel_type',models.CharField(blank=True,choices=[('OCTANE','Octane / অকটেন'),('PETROL','Petrol / পেট্রোল'),('DIESEL','Diesel / ডিজেল'),('CNG','CNG / সিএনজি'),('LPG','LPG / এলপিজি'),('ELECTRIC','Electric / বিদ্যুৎ')],max_length=16)),
            ('quantity',models.DecimalField(blank=True,decimal_places=2,max_digits=10,null=True,validators=[django.core.validators.MinValueValidator(0.01)])),
            ('odometer',models.PositiveIntegerField(blank=True,null=True)),
            ('receipt_photo',models.ImageField(blank=True,null=True,upload_to='receipts/')),
            ('meter_photo',models.ImageField(blank=True,null=True,upload_to='meters/')),
            ('notes',models.TextField(blank=True,max_length=1000)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='expenses',to=settings.AUTH_USER_MODEL)),
            ('vehicle',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='expenses',to='ledger.vehicle')),
        ],options={'ordering':['-date','-id']}),
        migrations.CreateModel(name='Reminder', fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('title',models.CharField(max_length=140)),
            ('due_date',models.DateField(blank=True,null=True)),
            ('due_odometer',models.PositiveIntegerField(blank=True,null=True)),
            ('done',models.BooleanField(default=False)),
            ('notes',models.CharField(blank=True,max_length=250)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('owner',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='reminders',to=settings.AUTH_USER_MODEL)),
            ('vehicle',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='reminders',to='ledger.vehicle')),
        ],options={'ordering':['done','due_date','id']}),
    ]
