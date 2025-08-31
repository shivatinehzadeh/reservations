from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_kafka():
    with patch("setup.kafka_setup.get_kafka_producer") as mock:
        producer = MagicMock()
        mock.return_value = producer
        yield producer


def test_kafka_producer_send_success(mock_kafka):
    message = {
        "reservation_id": "resv_123",
        "created_at": "2025-10-10T10:00:00Z",
        "event_type": "Reservation Created",
    }
    mock_kafka.send("reservations", value=message)
    mock_kafka.flush()

    mock_kafka.send.assert_called_once_with("reservations", value=message)
    mock_kafka.flush.assert_called_once()


def test_kafka_producer_send_failed(mock_kafka):
    message = {"reservation_id": "resv_123"}
    mock_kafka.send = MagicMock(side_effect=Exception("Kafka down"))
    mock_kafka.flush = MagicMock()

    with pytest.raises(Exception) as exc_info:
        mock_kafka.send("reservations", value=message)

    assert str(exc_info.value) == "Kafka down"
