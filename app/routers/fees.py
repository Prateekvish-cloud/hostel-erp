from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.fees import (
    FeeRecordDB,
    PaymentDB,
    FeeRecord,
    Payment,
    SetDueRequest,
    PayRequest,
)
from app.routers.auth import get_current_user  # <-- real auth


router = APIRouter(prefix="/api/fees", tags=["fees"])


# ---- helpers ----

def _to_fee_record_schema(record: FeeRecordDB) -> FeeRecord:
    payments = [
        Payment(amount=p.amount, timestamp=p.timestamp)
        for p in sorted(record.payments, key=lambda x: x.timestamp)
    ]
    return FeeRecord(username=record.username, total_due=record.total_due, payments=payments)


# ---- endpoints ----

@router.post("/set-due", response_model=FeeRecord)
def set_due(
    req: SetDueRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # admin sets or updates hostel fee due for a student
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can set dues")

    record = (
        db.query(FeeRecordDB)
        .filter(FeeRecordDB.username == req.username)
        .first()
    )
    if record is None:
        record = FeeRecordDB(username=req.username, total_due=req.amount)
        db.add(record)
    else:
        record.total_due = req.amount

    db.commit()
    db.refresh(record)

    return _to_fee_record_schema(record)


@router.post("/pay", response_model=FeeRecord)
def pay(
    req: PayRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # admin records a payment
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can record payments")

    record = (
        db.query(FeeRecordDB)
        .filter(FeeRecordDB.username == req.username)
        .first()
    )
    if record is None:
        record = FeeRecordDB(username=req.username, total_due=0.0)
        db.add(record)
        db.commit()
        db.refresh(record)

    payment = PaymentDB(
        fee_record_id=record.id,
        amount=req.amount,
        timestamp=datetime.utcnow(),
    )
    db.add(payment)

    record.total_due = max(record.total_due - req.amount, 0.0)

    db.commit()
    db.refresh(record)

    return _to_fee_record_schema(record)


@router.get("/all", response_model=List[FeeRecord])
def list_all_fees(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view all fees")

    records = db.query(FeeRecordDB).all()
    return [_to_fee_record_schema(r) for r in records]


@router.get("/my", response_model=FeeRecord)
def my_fees(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    username = user["username"]
    record = (
        db.query(FeeRecordDB)
        .filter(FeeRecordDB.username == username)
        .first()
    )
    if record is None:
        return FeeRecord(username=username, total_due=0.0, payments=[])

    return _to_fee_record_schema(record)
