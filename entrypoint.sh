#!/bin/sh
set -e

echo "[Alembic] Ejecutando migraciones..."
alembic upgrade head
echo "[Alembic] Migraciones completadas"

exec uvicorn app.main:app --host 0.0.0.0 --port 3004
