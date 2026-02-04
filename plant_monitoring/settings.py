# plant_monitoring/settings.py

import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# ... (остальные настройки)

INSTALLED_APPS = [
    # ...
    'rest_framework',
    'sensor.apps.SensorConfig', # Добавляем наше приложение
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