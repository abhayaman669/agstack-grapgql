from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import config
from app.helpers.jwt_helper import verify_jwt
from app.db.mongodb import get_database, AsyncIOMotorClient


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
async def list_users(
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

    users_list = db[config.db_name][config.user_collection_name].find()

    users_coll = []
    async for user in users_list:
        users_coll.append({
            "username": user["username"],
            "user_id": str(user["_id"])
        })

    return {
        "status": "Success",
        "users": users_coll
    }
