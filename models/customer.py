from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel,EmailStr

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    reservation = relationship("Reservation", back_populates="customer")
    
    
class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class CustomerRead(CustomerCreate):
    id: int

    model_config = {
        "from_attributes": True
    }