from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from setup.database_setup import Base


class Guests(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    reservation = relationship("Reservations", back_populates="guest")


NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class GuestCreate(BaseModel):
    first_name: NonEmptyStr
    last_name: NonEmptyStr
    email: EmailStr


class GuestRead(GuestCreate):
    id: int

    model_config = {"from_attributes": True}
