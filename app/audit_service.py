from fastapi import HTTPException

from models import AuditLog
from setup.kafka_setup import get_kafka_consumer
from setup.logger import get_logger

audit_logger = get_logger("audit_log", "audit_log.log")


def audit_service(db):
    try:
        kafka_consumer_messages = get_kafka_consumer()
        audit_logger.info("Starting Kafka consumer for audit service...")
        for message in kafka_consumer_messages:
            data = message.value
            audit_logger.info(f"Received message: {data}")
            audit_log(data, db)
    except Exception as e:
        audit_logger.error(f"Error in audit service: {e}")
        pass


def audit_log(data: dict, db):
    try:
        audit_log = AuditLog(
            reservation_id=data.get("reservation_id"),
            event_type=data.get("event_type"),
            created_at=data.get("created_at"),
        )
        db.add(audit_log)
        db.commit()
        audit_logger.info(f"Audit log created with ID: {audit_log.id}")
    except Exception as e:
        db.rollback()
        audit_logger.error(f"Error creating audit log: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal Server Error in audit log creation"},
        )
