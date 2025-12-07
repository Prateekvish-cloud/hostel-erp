from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from pydantic import BaseModel, computed_field


# ---------- SQLAlchemy ORM model (DB table) ----------

class RoomDB(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(String(50), unique=True, index=True, nullable=False)
    block = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(50), nullable=False, default="normal")
    # For now, store occupants count or handle occupants in a separate table later.
    # Here we just keep capacity; occupancy will be calculated from allocations table later.


# ---------- Pydantic schemas (request/response) ----------

class RoomBase(BaseModel):
    room_number: str
    block: str
    capacity: int
    room_type: str = "normal"


class RoomCreate(RoomBase):
    pass


class RoomRead(RoomBase):
    id: int

    @computed_field
    @property
    def vacant_beds(self) -> int:
        # For now assume 0 occupants; later link to allocations.
        return self.capacity

    @computed_field
    @property
    def status(self) -> str:
        # With real occupants this will change; for now everything is vacant.
        return "vacant"

    class Config:
        from_attributes = True  # allow creating from SQLAlchemy model
