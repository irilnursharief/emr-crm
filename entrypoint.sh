#!/bin/bash
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do sleep 0.1; done
echo "PostgreSQL is up"

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput

# Run Gunicorn WSGI server
exec uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120