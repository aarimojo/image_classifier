from app import db
from app.user import hashing
from app.user.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from loguru import logger

from .jwt import create_access_token

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)
):
    logger.info(f"Logging in with username: {request.username}")
    user = db.query(User).filter(User.email == request.username).first()

    if not user:
        logger.error(f"User not found: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid credentials"
        )
    if not hashing.verify_password(request.password, user.password):
        logger.error(f"Incorrect password for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password"
        )

    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Login successful for user: {request.username}")
    return {"access_token": access_token, "token_type": "bearer"}
