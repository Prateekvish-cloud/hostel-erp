from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Hostel ERP System")

app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Hostel ERP Backend is running"}
