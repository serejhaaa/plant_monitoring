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

| Модель                   | Таблица                      | Описание |
|--------------------------|------------------------------|----------|
| MeasurementType          | measurement_type             | Тип измерения (id, name, code) |
| Board                    | board                        | Плата (id, name, secret_token, serial_number, rgb_config JSON, is_activated) |
| SensorModel              | sensor_model                 | Модель датчика (name, description, default_config JSON, M2M measurement_types) |
| SensorModelMeasurementType | sensor_model_measurement_type | Связь SensorModel ↔ MeasurementType |
| Sensor                   | sensor                       | Датчик (board, sensor_model, config JSON) |
| Measurement              | sensor_measurement           | Показание (value, sensor, measurement_type) |

## API

- **CRUD** (boards, sensors, sensor-models, measurement-types) — `X-SECRET-TOKEN` (admin)
- **Конфиг платы** — `GET /api/board/config/<serial_number>/` без авторизации. Возвращает конфиг только при is_activated=False, затем ставит is_activated=True
- **Отправка измерений** — `POST /api/board/measure/`, токен платы в заголовке. Тело: `[{"sensor_uuid","measurement_type_uuid","value"},...]`

Эндпоинты: `/api/boards/`, `/api/sensors/`, `/api/sensor-models/`, `/api/measurement-types/`, `/api/board/config/<sn>/`, `/api/board/measure/`, `/api/measurements/`

## Прошивка ESP32

- `main.py` — загрузка конфига, WiFi, fallback AP
- При отсутствии WiFi — точка доступа PlantMonitor, веб-страница настройки (серийник, WiFi, URL сервера)
- `config.json` / `config.default.json`

## Важные решения

- Токен платы генерируется автоматически при создании (128 hex-символов)
- У всех сущностей UUID
- Таблицы: board, sensor (не sensor_board, sensor_sensor)

## Деплой

Push в ветку dev → GitHub Actions → VPS (Gunicorn, nginx). БД создаётся вручную через `scripts/setup_postgres.sh`. Папка `firmware/` исключается при деплое. Миграции создаются локально (makemigrations не запускается на сервере).
