from celery.app import Celery
from datetime import datetime
import os

# redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# CELERY_BROKER_URL = "sqla+sqlite:////your/project/path/broker.sqlite3"
# RESULT_BACKEND_URL = "db+sqlite:////n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/results.sqlite3"
# BROKER_URL = "db+sqlite:////n/holylabs/LABS/olveczky_lab/Lab/dannce-dev/newsdannce/src/gui_be/instance_data/broker.sqlite3"

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
