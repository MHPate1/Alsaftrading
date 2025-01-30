FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=perfume_store.settings
ENV PORT 8080

# Set work directory
WORKDIR /app

# Copy project
COPY . /app/

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    && python manage.py collectstatic --noinput

# Make start script executable
COPY start.sh .
RUN chmod +x start.sh

# Port exposure
EXPOSE ${PORT}

# Start command
CMD exec gunicorn --bind :${PORT} --workers 3 --threads 8 --timeout 0 perfume_store.wsgi:application