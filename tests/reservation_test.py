from unittest.mock import MagicMock

from setup.base import app
from setup.database_setup import get_db

mock_db = MagicMock()


def test_create_reservation_success(client):
    payload = {
        "reservation_id": "resv_123456",
        "room": "101",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-10-10T17:00:00Z",
        "guest": {
            "first_name": "Anna",
            "last_name": "M.",
            "email": "anna.m@example.com",
        },
        "source": "booking-com",
    }

    response = client.post("/reservations", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "reservation_id" in data
    assert data["message"] == "Reservation created successfully"


def test_create_reservation_start_and_end_time_failed(client):
    payload = {
        "reservation_id": "resv_123456",
        "room": "101",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-09-11T11:00:00Z",
        "guest": {
            "first_name": "Anna",
            "last_name": "M.",
            "email": "anna.m@example.com",
        },
        "source": "booking-com",
    }

    response = client.post("/reservations", json=payload)
    assert response.status_code == 400

    data = response.json()
    assert data["message"] == "start_time must be before end_time."


def test_create_reservation_start_time_failed(client):
    payload = {
        "reservation_id": "resv_123456",
        "room": "101",
        "start_time": "2024-10-10T15:00:00Z",
        "end_time": "2026-10-11T11:00:00Z",
        "guest": {
            "first_name": "Anna",
            "last_name": "M.",
            "email": "anna.m@example.com",
        },
        "source": "booking-com",
    }

    response = client.post("/reservations", json=payload)
    assert response.status_code == 400
    data = response.json()
    
    message = "Please provide a valid start time that is today or later than the current time."
    assert data["message"] == message


def test_create_reservation_duplicate_email_failed(client):
    payload = {
        "reservation_id": "resv_123456",
        "room": "101",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-10-12T11:00:00Z",
        "guest": {
            "first_name": "Anna",
            "last_name": "M.",
            "email": "anna.m@example.com",
        },
        "source": "booking-com",
    }
    response = client.post("/reservations", json=payload)
    assert response.status_code == 201

    duplicate_payload = {
        "reservation_id": "resv_123457",
        "room": "102",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-10-12T11:00:00Z",
        "guest": {
            "first_name": "Bob",
            "last_name": "S.",
            "email": "anna.m@example.com",
        },
        "source": "booking-com",
    }

    response_duplicate = client.post("/reservations", json=duplicate_payload)
    assert response_duplicate.status_code == 400

    data = response_duplicate.json()
    assert data["detail"]["message"] == "Guest email already exists."


def test_create_reservation_duplicate_reservation_failed(client):
    payload = {
        "reservation_id": "resv_123456",
        "room": "101",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-10-12T11:00:00Z",
        "guest": {
            "first_name": "Anna",
            "last_name": "M.",
            "email": "anna.m@example.com",
        },
        "source": "booking-com",
    }

    response = client.post("/reservations", json=payload)
    assert response.status_code == 201

    response_duplicate = client.post("/reservations", json=payload)
    assert response_duplicate.status_code == 400

    data = response_duplicate.json()
    assert data["detail"]["message"] == "Reservation ID already exists."


def test_create_reservation_validation_failed(client):
    invalid_payload = {
        "reservation_id": 123456,
        "room": 101,
        "start_time": "",
        "end_time": "invalid-date",
        "guest": {"first_name": 111, "last_name": 00, "email": ""},
        "source": 123,
    }
    response_duplicate = client.post("/reservations", json=invalid_payload)
    data = response_duplicate.json()

    assert response_duplicate.status_code == 422
    assert "detail" in data
    assert len(data["detail"]) >= 1

    checked_fields = [
        "email",
        "first_name",
        "start_time",
        "room",
        "source",
        "reservation_id",
        "end_time",
        "last_name",
    ]
    for item in data["detail"]:
        assert item["loc"][-1] in checked_fields
        checked_fields.remove(item["loc"][-1])
    assert len(checked_fields) == 0


def test_guest_internal_server_error(client):
    payload = {
        "reservation_id": "resv_123",
        "room": "101",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-10-12T10:00:00Z",
        "guest": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        },
        "source": "booking-com",
        "created_at": "2025-06-10T14:00:00Z",
    }

    mock_db.query().filter().first.return_value = None

    def add_side_effect(obj):
        if hasattr(obj, "first_name"):
            raise Exception("Simulated internal error")
        return None

    mock_db.add.side_effect = add_side_effect
    mock_db.commit.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/reservations", json=payload)

    assert response.status_code == 500
    assert response.json() == {
        "detail": {"message": "Internal Server Error in Guest creation"}
    }

    app.dependency_overrides.clear()


def test_reservation_internal_server_error(client):
    payload = {
        "reservation_id": "resv_123",
        "room": "101",
        "start_time": "2025-10-10T15:00:00Z",
        "end_time": "2025-10-12T10:00:00Z",
        "guest": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        },
        "source": "booking-com",
        "created_at": "2025-06-10T14:00:00Z",
    }

    def add_side_effect(obj):
        if hasattr(obj, "reservation_id"):
            raise Exception("Simulated internal error")
        return None

    mock_db.add.side_effect = add_side_effect

    mock_db.commit.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post("/reservations", json=payload)

    assert response.status_code == 500
    assert response.json() == {
        "detail": {"message": "Internal Server Error in Reservation creation"}
    }

    app.dependency_overrides.clear()
