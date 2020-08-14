import jwt
import bcrypt
from fastapi import APIRouter
from pydantic import BaseModel

from app import get_db
from app.config import config


router = APIRouter()


class UserData(BaseModel):
    username: str
    password: str
    token: str


@router.post("/")
async def login(user_data: UserData):

    # Validating token
    if user_data.token != config.token:
        return {
            "status": "Failed",
            "detail": "Invalid token"
        }

    db = get_db()
    users = db.users

    # Validating username
    user = users.find_one({"username": user_data.username})
    if not user:
        return {
            "status": "Failed",
            "detail": "Invalid username"
        }

    # Validating password
    if not bcrypt.checkpw(user_data.password, user["password"]):
        return {
            "status": "Failed",
            "detail": "Invalid password"
        }

    # Generating access_token
    access_token = jwt.encode(
            {"username": user["username"]},
            key=config.jwt_secret_key
    ).decode("utf-8")

    return {
        "status": "Success",
        "access_token": access_token
    }
