#!/bin/bash
# Одноразовая настройка PostgreSQL. Запускать на сервере вручную с sudo.
# Использование (на сервере):
#   sudo -u postgres bash scripts/setup_postgres.sh mydb myuser mypassword

set -e
DB_NAME=${1:?"Usage: $0 DB_NAME DB_USER DB_PASSWORD"}
DB_USER=${2:?}
DB_PASSWORD=${3:?}

echo "Creating user $DB_USER..."
psql -v ON_ERROR_STOP=1 <<EOSQL
  CREATE USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
  CREATE DATABASE "$DB_NAME" OWNER "$DB_USER";
  GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOSQL

echo "Done. Database '$DB_NAME' and user '$DB_USER' created."
