#!/usr/bin/env bash
# scripts/entrypoint.sh
set -e

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static..."
python manage.py collectstatic --noinput

echo "🌐 Compiling messages..."
python manage.py compilemessages || true

echo "🚀 Starting Daphne..."
exec daphne -b 0.0.0.0 -p 8001 config.asgi:application