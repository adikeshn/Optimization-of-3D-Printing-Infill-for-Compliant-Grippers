#!/bin/bash
set -e

celery -A celery_app worker --loglevel=info --concurrency=1 --max-tasks-per-child=1 &

exec gunicorn app:app --bind 0.0.0.0:10000 --timeout 120 --workers 1