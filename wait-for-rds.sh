#!/bin/sh
set -e

: "${DB_HOST:?Need to set DB_HOST}"
: "${DB_PORT:?Need to set DB_PORT}"
: "${DB_USER:?Need to set DB_USER}"
: "${DB_PASSWORD:?Need to set DB_PASSWORD}"
: "${DB_NAME:?Need to set DB_NAME}"

echo "Waiting for RDS at $DB_HOST:$DB_PORT (db=$DB_NAME, user=$DB_USER)..."
export PGPASSWORD="$DB_PASSWORD"

until psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  >&2 echo "RDS is unavailable - sleeping 3s"
  sleep 3
done

>&2 echo "RDS is up - executing: $*"
exec "$@"
