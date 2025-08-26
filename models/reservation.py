from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from .guest import GuestCreate, GuestRead

class Reservations(Base):
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, unique=True,nullable=False)
    room = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    guest = relationship("Guest", back_populates="reservation")
    audit = relationship("Audit", back_populates="reservation")


class ReservationCreate(BaseModel):
    room: int
    start_time: datetime
    end_time: datetime
    source: str
    created_at: datetime
    guest: GuestCreate
    
class ReservationRead(BaseModel):
    id: int
    room: int
    start_time: datetime
    end_time: datetime
    source: str
    created_at: datetime
    guest: GuestRead

    model_config = {
        "from_attributes": True
    }