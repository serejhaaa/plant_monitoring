# sensor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/measure/', views.add_measurement, name='add_measurement'),
    path('api/measurements/', views.list_measurements, name='list_measurements'),
]