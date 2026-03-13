# Generated migration - extend models

import uuid
import django.db.models.deletion
from django.db import migrations, models


def generate_serial_for_boards(apps, schema_editor):
    Board = apps.get_model('sensor', 'Board')
    for b in Board.objects.all():
        b.serial_number = str(b.id)
        b.save()


def reverse_noop(apps, schema_editor):
    pass


def migrate_sensors_to_model(apps, schema_editor):
    Sensor = apps.get_model('sensor', 'Sensor')
    SensorModel = apps.get_model('sensor', 'SensorModel')
    if Sensor.objects.exists():
        legacy, _ = SensorModel.objects.get_or_create(
            name='Legacy',
            defaults={'description': 'Migrated from sensor_type'}
        )
        Sensor.objects.filter(sensor_model__isnull=True).update(sensor_model=legacy)


class Migration(migrations.Migration):

    dependencies = [
        ('sensor', '0004_add_sensor_to_measurement'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'db_table': 'measurement_type',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SensorModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True)),
                ('default_config', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'db_table': 'sensor_model',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='board',
            name='serial_number',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='board',
            name='rgb_config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='board',
            name='is_activated',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(generate_serial_for_boards, reverse_noop),
        migrations.AlterField(
            model_name='board',
            name='serial_number',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='SensorModelMeasurementType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measurement_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensor_model_links', to='sensor.measurementtype')),
                ('sensor_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_measurement_types', to='sensor.sensormodel')),
            ],
            options={
                'db_table': 'sensor_model_measurement_type',
                'unique_together': {('sensor_model', 'measurement_type')},
            },
        ),
        migrations.AddField(
            model_name='sensormodel',
            name='measurement_types',
            field=models.ManyToManyField(blank=True, related_name='sensor_models', through='sensor.SensorModelMeasurementType', to='sensor.measurementtype'),
        ),
        migrations.AddField(
            model_name='sensor',
            name='sensor_model',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='sensor.sensormodel'),
        ),
        migrations.RunPython(migrate_sensors_to_model, reverse_noop),
        migrations.RemoveField(
            model_name='sensor',
            name='sensor_type',
        ),
        migrations.AlterField(
            model_name='sensor',
            name='sensor_model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='sensor.sensormodel'),
        ),
        migrations.AddField(
            model_name='sensor',
            name='config',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='measurements', to='sensor.measurementtype'),
        ),
    ]
