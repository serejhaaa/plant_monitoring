# Прошивка Plant Monitor — ESP32 (MicroPython)

## Файлы

- `main.py` — основная прошивка
- `config.default.json` — шаблон конфига (копируется при первом запуске)
- `config.json` — рабочий конфиг (создаётся после настройки)

## Первый запуск

1. Залей MicroPython на ESP32.
2. Скопируй `main.py` и `config.default.json` на устройство (mpremote, ampy, Thonny).
3. Запусти `main.py`.
4. Плата поднимет WiFi `PlantMonitor` (пароль: `plant12345678`).
5. Открой в браузере `http://192.168.4.1`.
6. Заполни форму (WiFi, сервер, имя платы), на странице отображается серийный номер ESP32.
7. Сохрани — плата перезагрузится и подключится к WiFi.

## Конфиг

```json
{
  "wifi_ssid": "...",
  "wifi_password": "...",
  "api_url": "https://...",
  "board_name": "...",
  "measure_interval_sec": 60
}
```
