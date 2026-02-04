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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Наш секретный токен для авторизации
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'my-super-secret-default-token')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'