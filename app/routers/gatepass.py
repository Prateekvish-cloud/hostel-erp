from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.gatepass import (
    GatePassDB,
    GatePass,
    CreateGatePassRequest,
    DecisionRequest,
)
from app.routers.auth import get_current_user  # real auth

router = APIRouter(prefix="/api/gatepass", tags=["gatepass"])


# ---- helpers ----

def _to_schema(gp: GatePassDB) -> GatePass:
    return GatePass(
        id=gp.id,
        student_username=gp.student_username,
        from_date=gp.from_date,
        to_date=gp.to_date,
        reason=gp.reason,
        status=gp.status,
        created_at=gp.created_at,
        decided_at=gp.decided_at,
    )


# ---- endpoints ----

@router.post("/", response_model=GatePass)
def create_gatepass(
    req: CreateGatePassRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # students create their own gate pass requests
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can request gate pass")

    gp = GatePassDB(
        student_username=user["username"],
        from_date=req.from_date,
        to_date=req.to_date,
        reason=req.reason,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(gp)
    db.commit()
    db.refresh(gp)

    return _to_schema(gp)


@router.get("/my", response_model=List[GatePass])
def my_gatepasses(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their gate passes")

    rows = (
        db.query(GatePassDB)
        .filter(GatePassDB.student_username == user["username"])
        .order_by(GatePassDB.created_at.desc())
        .all()
    )
    return [_to_schema(r) for r in rows]


@router.get("/", response_model=List[GatePass])
def list_all(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # admin sees all gate passes
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view all gate passes")

    rows = db.query(GatePassDB).order_by(GatePassDB.created_at.desc()).all()
    return [_to_schema(r) for r in rows]


@router.post("/{gatepass_id}/decide", response_model=GatePass)
def decide_gatepass(
    gatepass_id: int,
    req: DecisionRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can decide gate passes")

    if req.status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    gp = db.query(GatePassDB).filter(GatePassDB.id == gatepass_id).first()
    if gp is None:
        raise HTTPException(status_code=404, detail="Gate pass not found")

    gp.status = req.status
    gp.decided_at = datetime.utcnow()

    db.commit()
    db.refresh(gp)

    return _to_schema(gp)
