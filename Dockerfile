# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /perfume_store

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copy requirements file
COPY requirements.txt /perfume_store/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /perfume_store/

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=perfume_store.settings
ENV DEBUG=False

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy entrypoint script
COPY start.sh /perfume_store/start.sh
RUN chmod +x /perfume_store/start.sh

# Expose port 8000
EXPOSE 8000

# Command to run the entrypoint script
CMD ["/perfume_store/start.sh"]
