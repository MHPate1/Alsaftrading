#!/bin/bash

echo "Starting container..."

echo "Collecting static files..."
python perfume_store/manage.py collectstatic --noinput

echo "Running migrations..."
python perfume_store/manage.py migrate --noinput

echo "Starting the application..."
cd perfume_store  # Add this line to change directory
exec gunicorn --bind $HOST:$PORT --workers 2 --threads 8 --timeout 0 perfume_store.wsgi:application