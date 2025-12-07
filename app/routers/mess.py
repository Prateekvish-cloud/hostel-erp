from datetime import date
from typing import List, Optional, Set

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.mess import (
    MEALS,
    DailyMenuDB,
    MealAttendanceDB,
    MealStatsDB,
    DailyMenu,
    MealAttendance,
    MealStats,
    MenuSetRequest,
    StatsSetRequest,
    AttendanceRequest,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/mess", tags=["mess"])


# ---------- helper converters ----------

def _items_to_str(items: List[str]) -> str:
    return ",".join(items)


def _items_from_str(s: str) -> List[str]:
    if not s:
        return []
    return s.split(",")


def _attendees_to_str(attendees: Set[str]) -> str:
    return ",".join(sorted(attendees))


def _attendees_from_str(s: str) -> Set[str]:
    if not s:
        return set()
    return set(s.split(","))


# ---------- menu endpoints ----------

@router.post("/menu", response_model=DailyMenu)
def set_menu(
    req: MenuSetRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can set menu")

    if req.meal not in MEALS:
        raise HTTPException(status_code=400, detail="Invalid meal")

    obj = (
        db.query(DailyMenuDB)
        .filter(DailyMenuDB.day == req.day, DailyMenuDB.meal == req.meal)
        .first()
    )
    if obj is None:
        obj = DailyMenuDB(day=req.day, meal=req.meal, items=_items_to_str(req.items))
        db.add(obj)
    else:
        obj.items = _items_to_str(req.items)

    db.commit()
    db.refresh(obj)

    return DailyMenu(day=obj.day, meal=obj.meal, items=_items_from_str(obj.items))


@router.get("/menu", response_model=List[DailyMenu])
def list_menus(
    day: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(DailyMenuDB)
    if day:
        q = q.filter(DailyMenuDB.day == day)
    rows = q.all()
    return [DailyMenu(day=r.day, meal=r.meal, items=_items_from_str(r.items)) for r in rows]


@router.get("/menu/today", response_model=List[DailyMenu])
def today_menu(
    today: date = date.today(),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(DailyMenuDB)
        .filter(DailyMenuDB.day == today)
        .all()
    )
    return [DailyMenu(day=r.day, meal=r.meal, items=_items_from_str(r.items)) for r in rows]


# ---------- attendance endpoints ----------

@router.post("/attendance", response_model=MealAttendance)
def mark_attendance(
    req: AttendanceRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can mark mess attendance")

    if req.meal not in MEALS:
        raise HTTPException(status_code=400, detail="Invalid meal")

    obj = (
        db.query(MealAttendanceDB)
        .filter(MealAttendanceDB.day == req.day, MealAttendanceDB.meal == req.meal)
        .first()
    )
    if obj is None:
        obj = MealAttendanceDB(day=req.day, meal=req.meal, attendees="")
        db.add(obj)

    attendees = _attendees_from_str(obj.attendees)
    if req.attending:
        attendees.add(user["username"])
    else:
        attendees.discard(user["username"])
    obj.attendees = _attendees_to_str(attendees)

    db.commit()
    db.refresh(obj)

    return MealAttendance(day=obj.day, meal=obj.meal, attendees=_attendees_from_str(obj.attendees))


@router.get("/attendance", response_model=List[MealAttendance])
def list_attendance(
    day: Optional[date] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their mess attendance")

    q = db.query(MealAttendanceDB)
    rows = q.all()
    rows = [r for r in rows if user["username"] in _attendees_from_str(r.attendees)]
    if day:
        rows = [r for r in rows if r.day == day]

    return [
        MealAttendance(day=r.day, meal=r.meal, attendees=_attendees_from_str(r.attendees))
        for r in rows
    ]


# ---------- stats endpoints ----------

@router.post("/stats", response_model=MealStats)
def set_stats(
    req: StatsSetRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can set mess stats")

    if req.meal not in MEALS:
        raise HTTPException(status_code=400, detail="Invalid meal")
    if req.plates_served > req.plates_prepared:
        raise HTTPException(status_code=400, detail="Served cannot exceed prepared")

    obj = (
        db.query(MealStatsDB)
        .filter(MealStatsDB.day == req.day, MealStatsDB.meal == req.meal)
        .first()
    )
    if obj is None:
        obj = MealStatsDB(
            day=req.day,
            meal=req.meal,
            plates_prepared=req.plates_prepared,
            plates_served=req.plates_served,
        )
        db.add(obj)
    else:
        obj.plates_prepared = req.plates_prepared
        obj.plates_served = req.plates_served

    db.commit()
    db.refresh(obj)

    return MealStats(
        day=obj.day,
        meal=obj.meal,
        plates_prepared=obj.plates_prepared,
        plates_served=obj.plates_served,
    )


@router.get("/stats", response_model=List[MealStats])
def list_stats(
    day: Optional[date] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view mess stats")

    q = db.query(MealStatsDB)
    if day:
        q = q.filter(MealStatsDB.day == day)
    rows = q.all()
    return [
        MealStats(
            day=r.day,
            meal=r.meal,
            plates_prepared=r.plates_prepared,
            plates_served=r.plates_served,
        )
        for r in rows
    ]
