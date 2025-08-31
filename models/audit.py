from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints
from sqlalchemy import Column, DateTime, Integer, String

from setup.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    reservation_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AuditLogCreate(BaseModel):
    event_type: NonEmptyStr
    reservation_id: int
    created_at: datetime


class AuditLogRead(AuditLogCreate):
    id: int

    model_config = {"from_attributes": True}
