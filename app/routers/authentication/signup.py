from uuid import uuid4

import bcrypt
from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.config import config
from app.db.mongodb import get_database, AsyncIOMotorClient
from app.helpers.users_helper import (
    check_user_with_email,
    check_user_with_username,
    create_new_user
)


router = APIRouter()


class UserData(BaseModel):
    username: str
    email: str
    password: str
    token: str


@router.post("/")
async def signup(
    user_data: UserData,
    db: AsyncIOMotorClient = Depends(get_database)
):

    # Validating token
    if user_data.token != config.token:
        return {
            "status": "Failed",
            "detail": "Invalid token"
        }

    # Validating email
    email_check = await check_user_with_email(db, user_data.email)
    username_check = await check_user_with_username(db, user_data.username)

    if email_check:
        return {
            "status": "Failed",
            "in": "email",
            "detail": "Email already in use."
        }
    elif username_check:
        return {
            "status": "Failed",
            "in": "username",
            "detail": "Username already in use."
        }

    # Checking password length
    if len(user_data.password) <= 8:
        return {
            "status": "Failed",
            "in": "password",
            "detail": "Password should be atleast 12 character long."
        }

    # Hashing password
    hash_password = bcrypt.hashpw(user_data.password, bcrypt.gensalt())

    # Creating user
    await create_new_user(
        db,
        user_data.username,
        user_data.email,
        hash_password
    )

    return {
        "status": "Success",
        "detail": "User created successfully."
    }
