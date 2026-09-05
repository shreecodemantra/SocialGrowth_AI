"""
Celery application wiring for the scheduler/publisher/analytics workers
(Phase 4+). Task modules are registered via `include=[...]` as each phase
adds them — the beat schedule stays empty until Phase 4 defines the
periodic publishing/metrics-collection jobs described in section 40.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "socialgrowth",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        # "app.workers.publishing_tasks",
        # "app.workers.analytics_tasks",
        # "app.workers.generation_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=30,
)

# Populated in Phase 4 with entries such as:
# celery_app.conf.beat_schedule = {
#     "collect-recent-metrics": {"task": "app.workers.analytics_tasks.collect_recent_metrics", "schedule": 900.0},
#     "publish-due-posts": {"task": "app.workers.publishing_tasks.publish_due_posts", "schedule": 60.0},
# }
celery_app.conf.beat_schedule = {}
