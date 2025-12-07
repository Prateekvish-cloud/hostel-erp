from datetime import date
from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.hostel_attendance import (
    HostelAttendanceDB,
    HostelAttendance,
    MarkRequest,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/hostel-attendance", tags=["hostel_attendance"])


# ---- helper functions ----

def _names_from_str(s: str) -> Set[str]:
    if not s:
        return set()
    return set(s.split(","))


def _names_to_str(names: Set[str]) -> str:
    return ",".join(sorted(names))


# ---- endpoints ----

@router.post("/mark", response_model=HostelAttendance)
def mark_attendance(
    req: MarkRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can mark hostel attendance")

    record = (
        db.query(HostelAttendanceDB)
        .filter(HostelAttendanceDB.day == req.day)
        .first()
    )
    if record is None:
        record = HostelAttendanceDB(day=req.day, present_usernames="")
        db.add(record)

    names = _names_from_str(record.present_usernames)
    if req.present:
        names.add(req.username)
    else:
        names.discard(req.username)
    record.present_usernames = _names_to_str(names)

    db.commit()
    db.refresh(record)

    return HostelAttendance(day=record.day, present_students=_names_from_str(record.present_usernames))


@router.get("/day", response_model=HostelAttendance)
def get_day_attendance(
    day: date,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view full day attendance")

    record = (
        db.query(HostelAttendanceDB)
        .filter(HostelAttendanceDB.day == day)
        .first()
    )
    if record is None:
        return HostelAttendance(day=day, present_students=set())

    return HostelAttendance(day=record.day, present_students=_names_from_str(record.present_usernames))


@router.get("/my", response_model=List[HostelAttendance])
def my_attendance(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their own attendance")

    username = user["username"]
    rows = db.query(HostelAttendanceDB).all()
    result: List[HostelAttendance] = []

    for r in rows:
        names = _names_from_str(r.present_usernames)
        if username in names:
            result.append(HostelAttendance(day=r.day, present_students=names))

    return result
