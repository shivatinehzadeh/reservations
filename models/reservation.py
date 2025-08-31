from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from setup.database import Base

from .guest import GuestCreate, GuestRead


class Reservations(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(String, unique=True, nullable=False)
    room = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    guest = relationship("Guests", back_populates="reservation")


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ReservationCreate(BaseModel):
    reservation_id: NonEmptyStr
    room: NonEmptyStr
    start_time: datetime
    end_time: datetime
    source: NonEmptyStr
    created_at: datetime = datetime.now()
    guest: GuestCreate


class ReservationRead(BaseModel):
    reservation_id: str
    room: str
    start_time: datetime
    end_time: datetime
    source: str
    created_at: datetime
    guest: GuestRead

    model_config = {"from_attributes": True}
