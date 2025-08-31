import time

from kafka.errors import NoBrokersAvailable

from app.audit_service import audit_service
from setup.database_setup import session_local
from setup.logger_setup import get_logger

audit_runner_logger = get_logger("audit_service_runner", "audit_service_runner.log")

max_retries = 20
retry_interval = 5

for attempt in range(1, max_retries + 1):
    try:
        audit_runner_logger.info("Starting audit service from consumer runner...")
        db = session_local()
        audit_service(db)
        break
    except NoBrokersAvailable:
        audit_runner_logger.warning(
            f"Kafka broker not ready,\
            retrying in {retry_interval}s..."
        )
        time.sleep(retry_interval)
    except Exception as e:
        audit_runner_logger.error(
            f"nexpected error starting consumer: {e}, retrying..."
        )
        time.sleep(retry_interval)
else:
    audit_runner_logger.critical(
        "Failed to connect to Kafka after maximum retries. Exiting."
    )
