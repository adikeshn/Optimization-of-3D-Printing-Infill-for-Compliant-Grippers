#!/bin/bash
set -e

celery -A celery_app worker --loglevel=info &

exec gunicorn app:app --bind 0.0.0.0:10000 --timeout 120