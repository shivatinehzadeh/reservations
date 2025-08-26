from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from .customer import CustomerCreate, CustomerRead

class Reservations(Base):
    __tablename__ = "reservations"
    
    reservation_id = Column(Integer, unique=True, primary_key=True, nullable=False)
    room = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="reservation")
    audit = relationship("Audit", back_populates="reservation")


class ReservationCreate(BaseModel):
    room: int
    start_time: datetime
    end_time: datetime
    source: str
    created_at: datetime
    guest: CustomerCreate
    
class ReservationRead(BaseModel):
    id: int
    room: int
    start_time: datetime
    end_time: datetime
    source: str
    created_at: datetime
    guest: CustomerRead

    model_config = {
        "from_attributes": True
    }