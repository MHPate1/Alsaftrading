#!/bin/bash

echo "Starting container..."

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting the application..."
exec gunicorn --bind $HOST:$PORT --workers 2 --threads 8 --timeout 0 perfume_store.wsgi:application