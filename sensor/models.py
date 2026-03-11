# sensor/models.py
import uuid
from django.db import models


class Board(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    secret_token = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        db_table = 'board'
        ordering = ['name']


class SensorType(models.TextChoices):
    AIR_TEMP = 'air_temp', 'Air Temperature'
    AIR_HUMIDITY = 'air_humidity', 'Air Humidity'
    SOIL_HUMIDITY = 'soil_humidity', 'Soil Humidity'


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='sensors')
    sensor_type = models.CharField(max_length=32, choices=SensorType.choices)

    def __str__(self):
        return f"{self.get_sensor_type_display()} on {self.board.name}"

    class Meta:
        db_table = 'sensor'
        ordering = ['board', 'sensor_type']


class Measurement(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.value}"

    class Meta:
        ordering = ['-timestamp']