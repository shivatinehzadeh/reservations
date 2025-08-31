import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from models import Guests, ReservationCreate, Reservations
from setup.database import get_db
from setup.kafka_setup import get_kafka_producer
from setup.logger import get_logger

router = APIRouter()

reservation_logger = get_logger("reservation", "reservation.log")
logger_kafka_producer = get_logger("kafka_producer", "kafka_producer.log")


@router.post("/reservations")
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    try:
        reservation_logger.info(f"Received reservation data: {dict(reservation)}")
        reservation_dict = dict(reservation)
        if reservation_dict.get("start_time") < datetime.now(
            reservation_dict.get("start_time").tzinfo
        ):
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Please provide a valid start time that is today or later than the current time."
                },
            )

        if reservation_dict.get("start_time") > reservation_dict.get("end_time"):
            return JSONResponse(
                status_code=400,
                content={"message": "start_time must be before end_time."},
            )

        # check if guest already exists/if not create new guest
        guest_data = dict(reservation_dict.pop("guest"))
        existing_guest = (
            db.query(Guests)
            .filter(
                Guests.first_name == guest_data["first_name"],
                Guests.last_name == guest_data["last_name"],
                Guests.email == guest_data["email"],
            )
            .first()
        )

        if existing_guest:
            db_guest = existing_guest
            reservation_logger.info(f"Existing guest found with ID: {db_guest.id}")
        else:
            db_guest = Guests(**guest_data)
            db.add(db_guest)
            db.flush()
            reservation_logger.info(f"Guest created with ID: {db_guest.id}")

    except IntegrityError as e:
        db.rollback()
        reservation_logger.error(f"Uniqueness error: {e.orig}")
        raise HTTPException(
            status_code=400, detail={"message": "Guest email already exists."}
        )

    except Exception as e:
        reservation_logger.error(f"Error creating reservation: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal Server Error in Guest creation"},
        )

    try:
        # insert reservation data
        reservation_dict["guest_id"] = db_guest.id
        db_reservation = Reservations(**reservation_dict)
        db.add(db_reservation)
        db.commit()
        reservation_logger.info(
            f"Reservation created with ID: {db_reservation.reservation_id}"
        )

    except IntegrityError as e:
        db.rollback()
        reservation_logger.error(f"Uniqueness error: {e.orig}")
        raise HTTPException(
            status_code=400, detail={"message": "Reservation ID already exists."}
        )
    except Exception as e:
        reservation_logger.error(f"Error creating reservation: {e}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal Server Error in Reservation creation"},
        )

    # Send data log to Kafka
    data_dict = {
        "event_type": "Reservation is created",
        "reservation_id": db_reservation.reservation_id,
        "created_at": db_reservation.created_at.isoformat(),
    }
    send_to_kafka(data_dict)

    return JSONResponse(
        status_code=201,
        content={
            "message": "Reservation created successfully",
            "reservation_id": db_reservation.reservation_id,
        },
    )


def send_to_kafka(data_dict: dict):
    try:

        logger_kafka_producer.info(f"Sending data to Kafka: {json.dumps(data_dict)}")
        kafka_producer = get_kafka_producer()
        kafka_producer.send("reservations", data_dict)
        kafka_producer.flush()
        logger_kafka_producer.info(
            "Data sent to Kafka topic reservations successfully."
        )

    except Exception as e:
        logger_kafka_producer.error(f"Error sending data to Kafka: {e}")
