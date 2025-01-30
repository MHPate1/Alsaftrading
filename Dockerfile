FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=perfume_store.settings
ENV DEBUG=False

WORKDIR /app

COPY . /app/

RUN apt-get update && apt-get install -y gcc libpq-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]
