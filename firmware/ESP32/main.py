"""
Plant Monitoring — прошивка ESP32 (MicroPython).
Загрузка конфига, WiFi, fallback AP с веб-страницей настройки.
"""
import gc
import json
import network
import socket
import machine
import utime
from binascii import hexlify

CONFIG_FILE = 'config.json'
CONFIG_DEFAULT = 'config.default.json'
AP_SSID = 'PlantMonitor'
AP_PASSWORD = 'plant12345678'
AP_IP = '192.168.4.1'
AP_PORT = 80


def get_serial():
    """Серийный номер (unique ID) ESP32."""
    try:
        return hexlify(machine.unique_id()).decode()
    except Exception:
        return None


def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            raw = f.read()
        if not raw or not raw.strip():
            raise ValueError('empty file')
        return json.loads(raw)
    except (OSError, ValueError):
        try:
            with open(CONFIG_DEFAULT, 'r') as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}


def save_config(cfg):
    """Запись конфига. Без indent — экономия памяти на ESP32."""
    data = json.dumps(cfg)
    with open(CONFIG_FILE, 'w') as f:
        f.write(data)


def wifi_connect(ssid, password, timeout_ms=15000):
    """Подключение к WiFi. Возвращает True при успехе."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    start = utime.ticks_ms()
    while utime.ticks_diff(utime.ticks_ms(), start) < timeout_ms:
        if wlan.status() == network.STAT_GOT_IP:
            return True
        utime.sleep_ms(100)
    return False


def start_ap():
    """Запуск точки доступа для настройки."""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    ap.ifconfig((AP_IP, '255.255.255.0', AP_IP, AP_IP))
    return ap


def make_html_page(serial, default_api_url=''):
    s = serial or '—'
    api_val = default_api_url.replace('"', '&quot;')
    return b'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plant Monitor — Настройка</title>
<style>
body{font-family:sans-serif;max-width:400px;margin:40px auto;padding:20px;background:#f5f5f5}
h1{font-size:1.2em;color:#333}
.box{background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 4px #ddd}
.serial{background:#eee;padding:10px;border-radius:4px;margin:10px 0;font-family:monospace;word-break:break-all}
label{display:block;margin-top:12px;color:#555;font-size:0.9em}
input{width:100%;padding:8px;margin-top:4px;box-sizing:border-box;border:1px solid #ccc;border-radius:4px}
button{width:100%;margin-top:20px;padding:12px;background:#4a90d9;color:#fff;border:none;border-radius:4px;font-size:1em;cursor:pointer}
button:hover{background:#357abd}
</style>
</head>
<body>
<div class="box">
<h1>Plant Monitor — Настройка</h1>
<p><strong>Серийный номер платы:</strong></p>
<div class="serial">''' + s.encode() + b'''</div>
<form method="post" action="/save">
<label>WiFi SSID</label>
<input name="wifi_ssid" type="text" required placeholder="Имя сети">
<label>Пароль WiFi</label>
<input name="wifi_password" type="text" placeholder="Пароль">
<label>URL сервера</label>
<input name="api_url" type="url" value="''' + api_val.encode() + b'''" placeholder="https://example.com">
<label>Имя платы</label>
<input name="board_name" type="text" placeholder="Теплица 1">
<button type="submit">Сохранить и перезагрузить</button>
</form>
</div>
</body>
</html>'''


def _unquote_plus(s):
    """Простой unquote_plus для form data."""
    s = s.replace('+', ' ')
    parts = []
    i = 0
    while i < len(s):
        if s[i:i+1] == '%' and i + 2 < len(s):
            try:
                parts.append(chr(int(s[i+1:i+3], 16)))
                i += 3
                continue
            except ValueError:
                pass
        parts.append(s[i])
        i += 1
    return ''.join(parts)


def parse_form_data(data):
    """Парсинг application/x-www-form-urlencoded."""
    result = {}
    for pair in data.split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            result[k] = _unquote_plus(v)
    return result


def run_setup_server(serial):
    """HTTP-сервер на странице настройки."""
    default_cfg = {}
    try:
        with open(CONFIG_DEFAULT, 'r') as f:
            default_cfg = json.load(f)
    except (OSError, ValueError):
        pass
    default_api = default_cfg.get('api_url', '')
    html = make_html_page(serial, default_api)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', AP_PORT))
    s.listen(2)

    print('AP: {}  IP: {}'.format(AP_SSID, AP_IP))
    print('Открой в браузере: http://' + AP_IP)

    while True:
        try:
            cl, addr = s.accept()
            req = cl.recv(2048).decode()
            if '/save' in req and 'POST' in req:
                idx = req.find('\r\n\r\n')
                if idx >= 0:
                    body = req[idx + 4:].strip()
                    form = parse_form_data(body)
                    cfg = load_config()
                    cfg['wifi_ssid'] = form.get('wifi_ssid', '')
                    cfg['wifi_password'] = form.get('wifi_password', '')
                    cfg['api_url'] = form.get('api_url', '')
                    cfg['board_name'] = form.get('board_name', '')
                    save_config(cfg)
                    cl.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n')
                    cl.send(b'<h1>OK. Перезагрузка через 2 сек...</h1>')
                    cl.close()
                    import time
                    time.sleep(2)
                    machine.reset()
            cl.send(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n')
            cl.send(html)
            cl.close()
        except Exception as e:
            print('Error:', e)
        gc.collect()


def main_loop(config):
    """Основной цикл (заглушка)."""
    print('WiFi OK. main_loop placeholder.')
    # TODO: опрос датчиков, отправка на сервер
    import time
    while True:
        time.sleep(config.get('measure_interval_sec', 60))


def main():
    gc.collect()
    serial = get_serial()
    print('Serial:', serial or 'N/A')

    config = load_config()
    ssid = config.get('wifi_ssid', '').strip()
    password = config.get('wifi_password', '')

    if ssid and wifi_connect(ssid, password):
        print('WiFi connected')
        main_loop(config)
    else:
        start_ap()
        run_setup_server(serial)


if __name__ == '__main__':
    main()
