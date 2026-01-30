#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
echo "================================ Sever is starting now  =================================="
python3 manage.py migrate &&

# Collect static files
echo "==========================👌🙏🔥 Collecting static files 👌🙏🔥========================"
python3 manage.py collectstatic --noinput &&

# Start Celery worker with your app's Celery instance
#echo "==========================👌🙏🔥 Starting Celery worker 👌🙏🔥========================"
celery -A project worker --loglevel=INFO &

# Start Flower monitoring
#echo "==========================👌🙏🔥 Starting Flower 👌🙏🔥=============================="
#celery -A app.celery_tasks.celery_app flower &
gunicorn project.wsgi:application --bind 0.0.0.0:8000 &
#python3 manage.py runserver 0.0.0.0:8000
