from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.audit_service import audit_service
from models import AuditLog

fake_message = MagicMock()
fake_message.value = {
    "reservation_id": "resv_123",
    "event_type": "Reservation Created",
    "created_at": datetime(2025, 6, 10, 15, 0, 0),
}


@pytest.fixture
def mock_kafka_consumer():
    return [fake_message]


def test_audit_service_success(db_session, mock_kafka_consumer):
    with patch(
        "app.audit_service.get_kafka_consumer", return_value=mock_kafka_consumer
    ):
        audit_service(db_session)
    log_query = db_session.query(AuditLog).filter_by(reservation_id="resv_123").first()

    assert log_query is not None
    assert log_query.event_type == "Reservation Created"


def test_audit_service_multiple_messages_success(db_session):
    messages = [
        MagicMock(
            value={
                "reservation_id": "resv_1",
                "event_type": "Created",
                "created_at": datetime(2025, 6, 10, 15, 0, 0),
            }
        ),
        MagicMock(
            value={
                "reservation_id": "resv_2",
                "event_type": "Updated",
                "created_at": datetime(2025, 6, 10, 15, 0, 0),
            }
        ),
    ]
    with patch("app.audit_service.get_kafka_consumer", return_value=messages):
        audit_service(db_session)

    logs_query = db_session.query(AuditLog).all()
    assert len(logs_query) == 2


def test_audit_service_invalid_message_failed(db_session):
    fake_message.value = {"event_type": "Reservation Created"}

    with patch("app.audit_service.get_kafka_consumer", [fake_message]):
        audit_service(db_session)

    saved_logs = db_session.query(AuditLog).all()
    assert len(saved_logs) == 0
