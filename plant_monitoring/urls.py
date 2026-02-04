# config/urls.py
from django.contrib import admin
from django.urls import path, include # Добавьте include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sensor.urls'))  # Подключаем URL-ы из приложения
]