from bson import ObjectId
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import config
from app.helpers.jwt_helper import verify_jwt
from app.db.mongodb import get_database, AsyncIOMotorClient


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
async def timesheet_events(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorClient = Depends(get_database)
):

    # verifing JWT
    jwt_data = verify_jwt(token)
    if not jwt_data:
        return {
            "status": "Failed",
            "details": "Invalid JWT"
        }

    user = await db[config.db_name][config.user_collection_name].find_one({
        "_id": ObjectId(jwt_data["user_id"])
    })

    if not user:
        return {
            "status": "Failed",
            "details": "No user found"
        }

    user["_id"] = str(user["_id"])
    del user["password"]

    return {
        "status": "Success",
        "details": user
    }

    return user
