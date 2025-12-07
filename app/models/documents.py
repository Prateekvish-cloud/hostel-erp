from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class DocumentDB(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), index=True, nullable=False)
    doc_type = Column(String(100), nullable=False)
    filename = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending / verified / rejected
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    comment = Column(String(1000), nullable=True)


class Document(BaseModel):
    id: int
    username: str
    doc_type: str
    filename: str
    status: str = "pending"
    uploaded_at: datetime
    verified_at: Optional[datetime] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class VerifyRequest(BaseModel):
    status: str  # "verified" or "rejected"
    comment: Optional[str] = None
