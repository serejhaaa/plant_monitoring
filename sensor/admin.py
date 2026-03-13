from django.contrib import admin
from .models import (
    MeasurementType,
    Board,
    SensorModel,
    SensorModelMeasurementType,
    Sensor,
    Measurement,
)


@admin.register(MeasurementType)
class MeasurementTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class SensorModelMeasurementTypeInline(admin.TabularInline):
    model = SensorModelMeasurementType
    extra = 0


@admin.register(SensorModel)
class SensorModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [SensorModelMeasurementTypeInline]


class SensorInline(admin.TabularInline):
    model = Sensor
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'serial_number', 'is_activated')
    inlines = [SensorInline]


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'sensor_model')
    list_select_related = ('board', 'sensor_model')


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'sensor', 'measurement_type', 'value')
    list_filter = ('timestamp',)
    list_select_related = ('sensor', 'measurement_type')
