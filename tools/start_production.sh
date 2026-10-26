#!/bin/sh
set -eu
mkdir -p "${DJANGO_MEDIA_ROOT:-/app/media}"
python manage.py setup_webpush
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-2}" --timeout 90 --access-logfile - --error-logfile -
