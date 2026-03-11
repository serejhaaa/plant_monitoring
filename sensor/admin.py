from django.contrib import admin
from .models import Board, Sensor, Measurement


class SensorInline(admin.TabularInline):
    model = Sensor
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [SensorInline]


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('id', 'board', 'sensor_type')
    list_filter = ('sensor_type',)
    list_select_related = ('board',)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'sensor', 'value')
    list_filter = ('timestamp',)
    search_fields = ('value',)
    ordering = ('-timestamp',)
