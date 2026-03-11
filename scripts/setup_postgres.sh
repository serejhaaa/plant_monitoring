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

  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
      EXECUTE format('CREATE DATABASE %I OWNER %I', '$DB_NAME', '$DB_USER');
      RAISE NOTICE 'Database $DB_NAME created';
    ELSE
      RAISE NOTICE 'Database $DB_NAME already exists';
    END IF;
  END \$\$;
  GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOSQL

echo "Done. Database '$DB_NAME' and user '$DB_USER' ready."
