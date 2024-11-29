#!/bin/bash

echo "Starting container..."

cd perfume_store

# Apply database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start the Django application
echo "Starting the application..."
gunicorn --bind 0.0.0.0:8080 perfume_store.wsgi:application
