from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from pydantic import BaseModel


# ---------- SQLAlchemy ORM model ----------

class MaintenanceTicketDB(Base):
    __tablename__ = "maintenance_tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_by = Column(String(255), nullable=False)     # username
    room_number = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=False)
    status = Column(String(50), nullable=False, default="open")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ---------- Pydantic schemas ----------

class TicketBase(BaseModel):
    room_number: str
    title: str
    description: str


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    status: Optional[str] = None       # open / in_progress / closed
    title: Optional[str] = None
    description: Optional[str] = None


class TicketRead(BaseModel):
    id: int
    created_by: str
    room_number: str
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
