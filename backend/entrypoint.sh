#!/bin/sh

# Ждем пока база данных станет доступной
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database started"

# Применяем миграции
python manage.py migrate

# Собираем статику
python manage.py collectstatic --noinput

# Запускаем Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000