from django.contrib import admin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('id', 'timestamp', 'value')
    list_filter = ('timestamp',)
    search_fields = ('value',)
    ordering = ('-timestamp',)
