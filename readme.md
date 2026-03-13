### Plant Monitoring

Django API для приёма измерений с датчиков.

#### Первоначальная настройка БД (один раз на сервере)

Подключись по SSH и выполни (подставь значения из GitHub Secrets):

```bash
cd /home/plant-deployer/plant_monitoring
sudo -u postgres bash scripts/setup_postgres.sh DB_NAME DB_USER DB_PASSWORD
```

Пример: `sudo -u postgres bash scripts/setup_postgres.sh plant_monitoring plant_deployer 'твой_пароль'`