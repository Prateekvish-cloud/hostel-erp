from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.rooms import RoomDB, RoomCreate, RoomRead
from app.models.users import UserDB
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


class AllocateRequest(BaseModel):
    username: str
    room_number: str


@router.post("/", response_model=RoomRead)
def create_room(
    data: RoomCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create rooms")

    existing = db.query(RoomDB).filter(RoomDB.room_number == data.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room already exists")

    room = RoomDB(
        room_number=data.room_number,
        block=data.block,
        capacity=data.capacity,
        room_type=data.room_type,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/", response_model=List[RoomRead])
def list_rooms(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rooms = db.query(RoomDB).all()
    return rooms


@router.post("/allocate", status_code=status.HTTP_200_OK)
def allocate_student(
    payload: AllocateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can allocate students")

    # 1. Find room
    room = db.query(RoomDB).filter(RoomDB.room_number == payload.room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # 2. Find user
    student = db.query(UserDB).filter(UserDB.username == payload.username).first()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Ensure occupants relationship exists (list of UserDB)
    if room.occupants is None:
        room.occupants = []

    # 4. Capacity check
    if len(room.occupants) >= room.capacity:
        raise HTTPException(status_code=400, detail="Room is already full")

    # 5. Prevent duplicates
    if student in room.occupants:
        raise HTTPException(status_code=400, detail="User already in this room")

    # 6. Allocate
    room.occupants.append(student)
    db.add(room)
    db.commit()
    db.refresh(room)

    return {"detail": "Student allocated successfully"}
