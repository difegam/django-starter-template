web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --chdir src
release: python src/manage.py migrate --noinput
