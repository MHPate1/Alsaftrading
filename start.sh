#!/bin/bash

echo "Starting container..."

cd perfume_store

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Launching application..."
gunicorn perfume_store.wsgi:application --bind 0.0.0.0:8080
