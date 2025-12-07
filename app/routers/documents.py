from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import os

from app.dependencies import get_db
from app.models.documents import DocumentDB, Document, VerifyRequest
from app.routers.auth import get_current_user  # real auth

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/api/documents", tags=["documents"])


# ---- helpers ----

def _to_schema(d: DocumentDB) -> Document:
    return Document(
        id=d.id,
        username=d.username,
        doc_type=d.doc_type,
        filename=d.filename,
        status=d.status,
        uploaded_at=d.uploaded_at,
        verified_at=d.verified_at,
        comment=d.comment,
    )


# ---- endpoints ----

@router.post("/upload", response_model=Document)
async def upload_document(
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # students upload their own documents
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can upload documents")

    ext = os.path.splitext(file.filename)[1]
    saved_name = f"{user['username']}_{int(datetime.utcnow().timestamp())}{ext}"
    full_path = os.path.join(UPLOAD_DIR, saved_name)
    with open(full_path, "wb") as f:
        f.write(await file.read())

    doc_db = DocumentDB(
        username=user["username"],
        doc_type=doc_type,
        filename=saved_name,
        status="pending",
        uploaded_at=datetime.utcnow(),
    )
    db.add(doc_db)
    db.commit()
    db.refresh(doc_db)

    return _to_schema(doc_db)


@router.get("/my", response_model=List[Document])
def my_documents(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view their documents")

    rows = (
        db.query(DocumentDB)
        .filter(DocumentDB.username == user["username"])
        .order_by(DocumentDB.uploaded_at.desc())
        .all()
    )
    return [_to_schema(r) for r in rows]


@router.get("/by-user/{username}", response_model=List[Document])
def documents_by_user(
    username: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view documents")

    rows = (
        db.query(DocumentDB)
        .filter(DocumentDB.username == username)
        .order_by(DocumentDB.uploaded_at.desc())
        .all()
    )
    return [_to_schema(r) for r in rows]


@router.post("/{doc_id}/verify", response_model=Document)
def verify_document(
    doc_id: int,
    req: VerifyRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can verify documents")

    if req.status not in {"verified", "rejected"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    doc_db = db.query(DocumentDB).filter(DocumentDB.id == doc_id).first()
    if doc_db is None:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_db.status = req.status
    doc_db.comment = req.comment
    doc_db.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(doc_db)

    return _to_schema(doc_db)
