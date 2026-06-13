#!/bin/sh
set -e

python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    if [ -n "$DJANGO_SUPERUSER_PASSWORD_FILE" ] && [ -f "$DJANGO_SUPERUSER_PASSWORD_FILE" ]; then
        su_password=$(cat "$DJANGO_SUPERUSER_PASSWORD_FILE")
        export DJANGO_SUPERUSER_PASSWORD="$su_password"
    fi

    if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        python src/manage.py createsuperuser \
            --noinput \
            --username "$DJANGO_SUPERUSER_USERNAME" \
            --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null || true
    fi
fi

exec "$@"
