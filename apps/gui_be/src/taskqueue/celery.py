from celery.app import Celery
from datetime import datetime
from app.core.config import settings
import os

from app.base_logger import logger

MAIN_QUEUE_NAME="dannce_gui"
RABBITMQ_NODE_PORT = os.environ.get("RABBITMQ_NODE_PORT", "5672")

print("USING RABBITMQ PORT: ", RABBITMQ_NODE_PORT)

BROKER_URL = f"amqp://localhost:{RABBITMQ_NODE_PORT}"
BACKEND_URL = f"rpc://localhost:{RABBITMQ_NODE_PORT}"

celery_app = Celery(
    MAIN_QUEUE_NAME, broker=BROKER_URL, backend=BACKEND_URL, 
    include=[
        "taskqueue.tasks",
        "taskqueue.video"
    ]
)
# include more apps if we want to

celery_app.conf.update(timezone="America/New_York")
celery_app.conf.update(broker_connection_retry_on_startup=True)
celery_app.conf.update(beat_schedule_filename=settings.CELERY_BEAT_FILES)

@celery_app.on_after_configure.connect
def add_periodic(**kwargs):
    from taskqueue.tasks import task_refresh_job_list
    logger.info("Refreshing job status every 60 seconds")
    celery_app.add_periodic_task(60, task_refresh_job_list.s(), name='Refresh jobs list')

if __name__ == "__main__":
    celery_app.start()
