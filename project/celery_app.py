from celery import Celery

celery = Celery(
    "infill_jobs",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)