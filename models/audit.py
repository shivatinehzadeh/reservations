from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from datetime import datetime


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    reservation_id = Column(Integer, ForeignKey("reservations.reservation_id"))
    created_at = Column(DateTime,nullable=False)
    payload = Column(JSON, nullable=False)
    reservation = relationship("Reservations", back_populates="audit")
    
class AuditLogCreate(BaseModel):
    event_type: str
    reservation_id: int
    created_at: datetime
    payload: dict

class AuditLogRead(AuditLogCreate):
    id: int

    model_config = {
        "from_attributes": True
    }