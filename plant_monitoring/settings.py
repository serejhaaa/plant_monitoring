# plant_monitoring/settings.py

import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# ... (остальные настройки)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # <-- УБЕДИТЕСЬ, ЧТО ЭТА СТРОКА ЕСТЬ
    'rest_framework',
    'sensor.apps.SensorConfig',
]

# ... (остальные настройки)

# Настройки БД через переменные окружения
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'sensor_db'),
        'USER': os.getenv('DB_USER', 'sensor_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Наш секретный токен для авторизации
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'my-super-secret-default-token')