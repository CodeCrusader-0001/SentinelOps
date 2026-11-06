from celery import Celery
from backend.app.core.config import settings
import redis

celery_app = Celery(
    "sentinelops",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend.app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,        # 5 minutes hard limit
    task_soft_time_limit=240,   # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_timeout=0.5,
    broker_connection_retry_on_startup=False,
    task_publish_retry=False,
    broker_transport_options={
        "max_retries": 0,
        "socket_timeout": 0.5,
        "socket_connect_timeout": 0.5
    }
)

def is_broker_available() -> bool:
    """Probes Redis broker with strict 0.2s timeout for instantaneous health check."""
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=0.2)
        return bool(r.ping())
    except Exception:
        return False
