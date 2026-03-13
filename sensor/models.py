# sensor/models.py
import uuid
from django.db import models


class MeasurementType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'measurement_type'
        ordering = ['name']


class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    secret_token = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, unique=True)
    rgb_config = models.JSONField(default=dict, blank=True)
    is_activated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        db_table = 'board'
        ordering = ['name']


class SensorModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    default_config = models.JSONField(default=dict, blank=True)
    measurement_types = models.ManyToManyField(
        MeasurementType,
        through='SensorModelMeasurementType',
        related_name='sensor_models',
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'sensor_model'
        ordering = ['name']


class SensorModelMeasurementType(models.Model):
    sensor_model = models.ForeignKey(
        SensorModel, on_delete=models.CASCADE, related_name='model_measurement_types'
    )
    measurement_type = models.ForeignKey(
        MeasurementType, on_delete=models.CASCADE, related_name='sensor_model_links'
    )

    class Meta:
        db_table = 'sensor_model_measurement_type'
        unique_together = [['sensor_model', 'measurement_type']]


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='sensors')
    sensor_model = models.ForeignKey(
        SensorModel, on_delete=models.CASCADE, related_name='sensors'
    )
    config = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.sensor_model.name} on {self.board.name}"

    class Meta:
        db_table = 'sensor'
        ordering = ['board', 'sensor_model']


class Measurement(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    sensor = models.ForeignKey(
        Sensor, on_delete=models.CASCADE, null=True, blank=True, related_name='measurements'
    )
    measurement_type = models.ForeignKey(
        MeasurementType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='measurements'
    )

    def __str__(self):
        return f"{self.timestamp} - {self.value}"

    class Meta:
        ordering = ['-timestamp']
