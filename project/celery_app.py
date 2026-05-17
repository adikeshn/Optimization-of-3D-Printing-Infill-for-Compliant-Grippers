import os
from celery import Celery

celery = Celery(
    "infill_jobs",
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    include=["tasks"],
)