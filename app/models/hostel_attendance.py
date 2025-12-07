from datetime import date
from typing import List, Set

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class HostelAttendanceDB(Base):
    __tablename__ = "hostel_attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day = Column(Date, nullable=False, index=True)
    present_usernames = Column(String(2000), nullable=False, default="")  # comma-separated usernames


class HostelAttendance(BaseModel):
    day: date
    present_students: Set[str]

    class Config:
        from_attributes = True


class MarkRequest(BaseModel):
    day: date
    username: str
    present: bool
