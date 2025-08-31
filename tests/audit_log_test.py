from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.audit_service import audit_log
from models import AuditLog


class FakeDBSession:
    def __init__(self):
        self.add = MagicMock()
        self.commit = MagicMock()
        self.refresh = MagicMock()
        self.rollback = MagicMock()
        self.close = MagicMock()


@pytest.fixture
def mock_db():
    return FakeDBSession()


def test_audit_log_success(db_session):
    audit_log(
        {
            "reservation_id": "resv_123",
            "event_type": "Reservation Created",
            "created_at": datetime(2025, 6, 10, 15, 0, 0),
        },
        db_session,
    )

    log_query = db_session.query(AuditLog).filter_by(reservation_id="resv_123").first()
    assert log_query is not None
    assert log_query.event_type == "Reservation Created"


def test_audit_log_internal_failed(mock_db):
    with patch("app.audit_service.audit_log", return_value=mock_db):
        mock_db.commit.side_effect = Exception("DB failure")

        with pytest.raises(HTTPException) as exc_info:
            audit_log(
                {
                    "reservation_id": "resv_123",
                    "event_type": "Reservation Created",
                    "created_at": "2025-06-10T15:00:00Z",
                },
                mock_db,
            )

        assert exc_info.value.status_code == 500
        assert (
            exc_info.value.detail["message"]
            == "Internal Server Error in audit log creation"
        )
