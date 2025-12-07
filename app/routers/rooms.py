from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.rooms import RoomDB, RoomCreate, RoomRead
from app.routers.auth import get_current_user  # add this

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
    # only admin can create rooms
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
    # any logged-in user can view rooms
    rooms = db.query(RoomDB).all()
    return rooms
