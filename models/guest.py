from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel,EmailStr

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    reservation = relationship("Reservation", back_populates="guest")
    
    
class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class GuestRead(GuestCreate):
    id: int

    model_config = {
        "from_attributes": True
    }