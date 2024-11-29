#!/bin/bash

echo "Starting container..."

# Apply database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start the Django application
echo "Starting the application..."
gunicorn --bind 0.0.0.0:8000 perfume_store.wsgi:application
