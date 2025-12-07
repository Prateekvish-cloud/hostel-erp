from datetime import datetime, date
from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, DateTime
from app.database import Base


class GatePassDB(Base):
    __tablename__ = "gatepasses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_username = Column(String(255), index=True, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    reason = Column(String(1000), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending / approved / rejected
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)


# ---------- Pydantic schemas ----------

class GatePass(BaseModel):
    id: int
    student_username: str
    from_date: date
    to_date: date
    reason: str
    status: str = "pending"
    created_at: datetime
    decided_at: datetime | None = None

    class Config:
        from_attributes = True


class CreateGatePassRequest(BaseModel):
    from_date: date
    to_date: date
    reason: str


class DecisionRequest(BaseModel):
    status: str  # approved or rejected
