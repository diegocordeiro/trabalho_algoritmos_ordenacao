#!/bin/bash
set -e

echo "==> Aplicando migracoes..."
python manage.py migrate --noinput

echo "==> Coletando arquivos estaticos..."
python manage.py collectstatic --noinput

echo "==> Iniciando Gunicorn..."
exec gunicorn projeto.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -