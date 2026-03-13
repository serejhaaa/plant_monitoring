# Plant Monitoring — Сводка проекта

## Цель проекта

Автоматизированные системы для домашних растений: фитостены, мониторинг условий, управление поливом и освещением. Сбор данных с датчиков (температура, влажность воздуха и почвы) и возможность расширения.

## Стек

- **Backend:** Python, Django, Django REST Framework
- **БД:** PostgreSQL
- **Деплой:** Gunicorn, systemd, GitHub Actions (ветка dev)
- **Устройства:** ESP32, MicroPython

## Структура репозитория

```
plant_monitoring/     # Django проект
sensor/               # Приложение: модели, API
scripts/              # setup_postgres.sh и др.
firmware/ESP32/       # Прошивка ESP32 (MicroPython)
docs/                 # Документация
.github/workflows/    # CI/CD
```

## Модели (sensor app)

| Модель      | Таблица  | Описание |
|-------------|----------|----------|
| Board       | board    | Плата (id UUID, name, secret_token 128 символов) |
| Sensor      | sensor   | Датчик (board FK, sensor_type: air_temp, air_humidity, soil_humidity) |
| Measurement | sensor_measurement | Показание (value, sensor FK, timestamp) |

## API

- **CRUD плат и сенсоров** — `X-SECRET-TOKEN` (глобальный admin токен из .env)
- **Отправка измерений платой** — `POST /api/board/measure/`, токен платы в заголовке
- **Типы сенсоров:** air_temp, air_humidity, soil_humidity

Эндпоинты: `/api/boards/`, `/api/sensors/`, `/api/board/measure/`, `/api/measurements/`.

## Прошивка ESP32

- `main.py` — загрузка конфига, WiFi, fallback AP
- При отсутствии WiFi — точка доступа PlantMonitor, веб-страница настройки (серийник, WiFi, URL сервера)
- `config.json` / `config.default.json`

## Важные решения

- Токен платы генерируется автоматически при создании (128 hex-символов)
- У всех сущностей UUID
- Таблицы: board, sensor (не sensor_board, sensor_sensor)

## Деплой

Push в ветку dev → GitHub Actions → VPS (Gunicorn, nginx). БД создаётся вручную через `scripts/setup_postgres.sh`.
