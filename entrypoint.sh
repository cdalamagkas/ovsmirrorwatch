#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
      echo "Waiting for postgres..."
    done

    echo "PostgreSQL started"
fi

python manage.py makemigrations --noinput

python manage.py migrate --noinput

if [ -n "$DJANGO_INITIALIZE_SUPERUSER" ] ; then
    python manage.py createsuperuser --no-input
fi

python manage.py collectstatic --noinput

daphne -b 0.0.0.0 -p 8000 ovsmirrorwatch.asgi:application