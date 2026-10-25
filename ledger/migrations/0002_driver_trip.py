from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ledger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(max_length=20, choices=[
                ('FUEL', 'Fuel / জ্বালানি'),
                ('MAINTENANCE', 'Maintenance / মেইনটেন্যান্স'),
                ('TRIP', 'Trip Cost / যাতায়াত'),
                ('TOLL', 'Toll / টোল'),
                ('PARKING', 'Parking / পার্কিং'),
                ('WASH', 'Car Wash / কার ওয়াশ'),
                ('TAX', 'Tax Token / ট্যাক্স টোকেন'),
                ('FITNESS', 'BRTA Fitness / ফিটনেস'),
                ('INSURANCE', 'Insurance / ইন্স্যুরেন্স'),
                ('OTHER', 'Other / অন্যান্য'),
            ]),
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('phone', models.CharField(max_length=20)),
                ('license_number', models.CharField(blank=True, max_length=80)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_vehicle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_drivers', to='ledger.vehicle')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drivers', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['name', 'id']},
        ),
    ]
