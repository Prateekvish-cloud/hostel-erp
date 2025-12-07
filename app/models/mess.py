from datetime import date
from typing import List, Set

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

MEALS = ["breakfast", "lunch", "dinner"]


# ---------- SQLAlchemy ORM models ----------

class DailyMenuDB(Base):
    __tablename__ = "daily_menus"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day = Column(Date, nullable=False, index=True)
    meal = Column(String(50), nullable=False, index=True)
    items = Column(String(2000), nullable=False)  # comma-separated list


class MealAttendanceDB(Base):
    __tablename__ = "meal_attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day = Column(Date, nullable=False, index=True)
    meal = Column(String(50), nullable=False, index=True)
    attendees = Column(String(2000), nullable=False, default="")  # comma-separated usernames


class MealStatsDB(Base):
    __tablename__ = "meal_stats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day = Column(Date, nullable=False, index=True)
    meal = Column(String(50), nullable=False, index=True)
    plates_prepared = Column(Integer, nullable=False)
    plates_served = Column(Integer, nullable=False)


# ---------- Pydantic schemas ----------

class DailyMenu(BaseModel):
    day: date
    meal: str
    items: List[str]

    class Config:
        from_attributes = True


class MealAttendance(BaseModel):
    day: date
    meal: str
    attendees: Set[str]

    class Config:
        from_attributes = True


class MealStats(BaseModel):
    day: date
    meal: str
    plates_prepared: int
    plates_served: int

    class Config:
        from_attributes = True


class MenuSetRequest(BaseModel):
    day: date
    meal: str
    items: List[str]


class StatsSetRequest(BaseModel):
    day: date
    meal: str
    plates_prepared: int
    plates_served: int


class AttendanceRequest(BaseModel):
    day: date
    meal: str
    attending: bool
