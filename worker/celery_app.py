"""Celery application configuration."""

from celery import Celery
from config.settings import settings

celery = Celery(
    "zeule",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=600,   # 10 min soft limit
    task_time_limit=900,        # 15 min hard limit
    beat_schedule={
        "sync-ad-performance": {
            "task": "worker.tasks.sync_ad_performance",
            "schedule": 3600.0,  # every hour
        },
    },
)

celery.autodiscover_tasks(["worker"])
