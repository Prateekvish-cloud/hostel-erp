from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.maintenance import (
    MaintenanceTicketDB,
    TicketCreate,
    TicketUpdate,
    TicketRead,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.post("/", response_model=TicketRead)
def create_ticket(
    data: TicketCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # only students create maintenance tickets
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can create tickets")

    now = datetime.utcnow()
    ticket = MaintenanceTicketDB(
        created_by=user["username"],
        room_number=data.room_number,
        title=data.title,
        description=data.description,
        status="open",
        created_at=now,
        updated_at=now,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/", response_model=List[TicketRead])
def list_all_tickets(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # admin sees all, students see only their own
    query = db.query(MaintenanceTicketDB)
    if user["role"] != "admin":
        query = query.filter(MaintenanceTicketDB.created_by == user["username"])

    return query.order_by(MaintenanceTicketDB.created_at.desc()).all()


@router.get("/my", response_model=List[TicketRead])
def list_my_tickets(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their tickets")

    return (
        db.query(MaintenanceTicketDB)
        .filter(MaintenanceTicketDB.created_by == user["username"])
        .order_by(MaintenanceTicketDB.created_at.desc())
        .all()
    )


@router.patch("/{ticket_id}", response_model=TicketRead)
def update_ticket(
    ticket_id: int,
    data: TicketUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(MaintenanceTicketDB)
        .filter(MaintenanceTicketDB.id == ticket_id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # student owner can edit description/status; admin can also update
    if user["role"] != "admin" and user["username"] != ticket.created_by:
        raise HTTPException(status_code=403, detail="Not allowed")

    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    ticket.updated_at = datetime.utcnow()
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
