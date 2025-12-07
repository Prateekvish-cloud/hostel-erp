from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models import rooms as rooms_models
from app.models import maintenance as maintenance_models   # NEW
from app.models import mess as mess_models
from app.models import hostel_attendance as hostel_attendance_models
from app.models import fees as fees_models
from app.models import gatepass as gatepass_models
from app.models import documents as documents_models

from app.routers import (
    auth,
    rooms,
    maintenance,
    mess,
    hostel_attendance,
    fees,
    gatepass,
    documents,
)

app = FastAPI(title="Hostel ERP System")

# Create database tables (rooms, maintenance, etc.)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(maintenance.router)
app.include_router(mess.router)
app.include_router(hostel_attendance.router)
app.include_router(fees.router)
app.include_router(gatepass.router)
app.include_router(documents.router)

# Static frontend – SERVE frontend AT ROOT
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
