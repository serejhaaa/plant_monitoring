# sensor/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/boards', views.BoardViewSet, basename='board')
router.register(r'api/sensors', views.SensorViewSet, basename='sensor')

urlpatterns = [
    path('', include(router.urls)),
    path('api/measure/', views.add_measurement, name='add_measurement'),
    path('api/measurements/', views.list_measurements, name='list_measurements'),
]