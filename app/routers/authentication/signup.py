from uuid import uuid4

import bcrypt
from fastapi import APIRouter
from pydantic import BaseModel

from app import get_db
from app.config import config


router = APIRouter()


class UserData(BaseModel):
    username: str
    email: str
    password: str
    token: str


@router.post("/")
async def signup(user_data: UserData):

    # Validating token
    if user_data.token != config.token:
        return {
            "status": "Failed",
            "detail": "Invalid token"
        }

    db = get_db()
    users = db.users

    # Validating email
    user = users.find_one({"email": user_data.email})
    if user:
        return {
            "status": "Failed",
            "in": "email",
            "detail": "Email already in use."
        }

    # Validating username
    user = users.find_one({"username": user_data.username})
    if user:
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
    doc = dict(
        id=str(uuid4()),
        username=user_data.username,
        email=user_data.email,
        password=hash_password
    )

    users.insert(doc)

    return {
        "status": "Success",
        "detail": "User created successfully."
    }
