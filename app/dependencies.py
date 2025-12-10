# app/routers/dependencies.py  (or app/core/dependencies.py in your imports)

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal          # your SQLAlchemy session factory
from app import models                         # your ORM models
from app.core import security                  # where you decode JWT tokens

# The same tokenUrl you use in your /api/token route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency: provide a database session and close it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """
    Dependency: get the current user from the JWT access token.
    """
    # security.decode_access_token should return {'sub': username} or raise
    try:
        payload = security.decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Dependency: ensure the current user is an admin.
    """
    # Adjust the field name (`role`, `is_admin`, etc.) to match your User model
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
