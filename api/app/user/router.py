from typing import List

from app import db
from app.auth.jwt import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from loguru import logger
from . import schema, services, validator

router = APIRouter(tags=["Users"], prefix="/user")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_registration(
    request: schema.User, database: Session = Depends(db.get_db)
):
    # TODO: Implement the create_user_registration endpoint
    # Make sure to:
    #  1. Verify the user email doesn't already exist, see `verify_email_exist()` function under `validator.py`
    #  2. If the email already exists, raise a 400 HTTPException
    #  3. If the email doesn't exist, create a new user, see `new_user_register()` function under `services.py`
    #  4. Return the new user object created
    logger.info(f"Creating user registration: {request}")
    if await validator.verify_email_exist(request.email, database):
        logger.error("Email already exists")
        raise HTTPException(status_code=400, detail="Email already exists")
    logger.info("Email does not exist, creating new user")
    new_user = await services.new_user_register(request, database)
    logger.info(f"New user created: {new_user}")
    return new_user


@router.get("/")
async def get_all_users(
    database: Session = Depends(db.get_db),
    current_user: schema.User = Depends(get_current_user),
):
    logger.info("Getting all users")
    return await services.all_users(database)


@router.get("/{id}", response_model=schema.DisplayUser)
async def get_user_by_id(
    id: int,
    database: Session = Depends(db.get_db),
    current_user: schema.User = Depends(get_current_user),
):
    logger.info(f"Getting user by id: {id}")
    logger.info(f"current_user jwt: {current_user}")
    return await services.get_user_by_id(id, database)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    id: int,
    database: Session = Depends(db.get_db),
    current_user: schema.User = Depends(get_current_user),
):
    logger.info(f"current_user jwt: {current_user}")
    logger.info(f"Deleting user by id: {id}")
    return await services.delete_user_by_id(id, database)
