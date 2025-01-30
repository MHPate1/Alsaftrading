#!/bin/bash

echo "Starting container..."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting the application..."
gunicorn perfume_store.wsgi:application --bind 0.0.0.0:$PORT