from datetime import datetime
from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class FeeRecordDB(Base):
    __tablename__ = "fee_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), index=True, nullable=False, unique=True)
    total_due = Column(Float, nullable=False, default=0.0)

    payments = relationship("PaymentDB", back_populates="fee_record", cascade="all, delete-orphan")


class PaymentDB(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fee_record_id = Column(Integer, ForeignKey("fee_records.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    fee_record = relationship("FeeRecordDB", back_populates="payments")


# ---------- Pydantic schemas ----------

class Payment(BaseModel):
    amount: float
    timestamp: datetime

    class Config:
        from_attributes = True


class FeeRecord(BaseModel):
    username: str
    total_due: float = 0.0
    payments: List[Payment] = []

    class Config:
        from_attributes = True


class SetDueRequest(BaseModel):
    username: str
    amount: float


class PayRequest(BaseModel):
    username: str
    amount: float
