from celery.app import Celery
from datetime import datetime
import os

RABBITMQ_NODE_PORT = os.environ.get("RABBITMQ_NODE_PORT", "5672")

print("USING RABBITMQ PORT: ", RABBITMQ_NODE_PORT)

BROKER_URL = f"amqp://localhost:{RABBITMQ_NODE_PORT}"
BACKEND_URL = f"rpc://localhost:{RABBITMQ_NODE_PORT}"

app = Celery(
    "dannce_gui", broker=BROKER_URL, backend=BACKEND_URL, include=["taskqueue.tasks"]
)

app.conf.update(timezone="America/New_York")
app.conf.update(broker_connection_retry_on_startup=True)


if __name__ == "__main__":
    app.start()
