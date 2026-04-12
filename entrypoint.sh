#!/bin/bash
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do sleep 0.1; done
echo "PostgreSQL is up"

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput

# Run Django development server
exec uv run python manage.py runserver 0.0.0.0:8000