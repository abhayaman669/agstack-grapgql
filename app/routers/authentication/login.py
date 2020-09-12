from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import config
from app.db.mongodb import get_database, AsyncIOMotorClient
from app.helpers.users_helper import get_authorize_user_jwt


router = APIRouter()


class UserData(BaseModel):
    username: str
    password: str
    token: str


@router.post("/")
async def login(
    user_data: UserData,
    db: AsyncIOMotorClient = Depends(get_database)
):

    # Validating token
    if user_data.token != config.token:
        return {
            "status": "Failed",
            "detail": "Invalid token"
        }

    # Validating username
    user = await get_authorize_user_jwt(
        db, user_data.username, user_data.password)

    return user
