from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.users import fake_users_db


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = fake_users_db.get(data.username)
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=access_token, role=user["role"])
