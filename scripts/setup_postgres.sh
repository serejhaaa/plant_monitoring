#!/bin/bash
# Настройка PostgreSQL (идемпотентный). Запускать на сервере вручную с sudo.
# Использование (на сервере):
#   sudo -u postgres bash scripts/setup_postgres.sh mydb myuser mypassword

set -e
DB_NAME=${1:?"Usage: $0 DB_NAME DB_USER DB_PASSWORD"}
DB_USER=${2:?}
DB_PASSWORD=${3:?}

psql -v ON_ERROR_STOP=1 <<EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$DB_USER') THEN
      CREATE USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
      RAISE NOTICE 'User $DB_USER created';
    ELSE
      ALTER USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';
      RAISE NOTICE 'User $DB_USER exists, password updated';
    END IF;
  END \$\$;
EOSQL

# CREATE DATABASE нельзя выполнять внутри функции — делаем отдельной командой
if ! psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
  psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"$DB_NAME\" OWNER \"$DB_USER\";"
  echo "Database $DB_NAME created"
else
  echo "Database $DB_NAME already exists"
fi

psql -v ON_ERROR_STOP=1 -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";"

echo "Done. Database '$DB_NAME' and user '$DB_USER' ready."
