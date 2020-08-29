from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app import get_db
from app.jwt_helper import verify_jwt, user_exists


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
async def list_users(token: str = Depends(oauth2_scheme)):
    # verifing JWT
    jwt_data = verify_jwt(token)
    if not jwt_data:
        return {
            "status": "Failed",
            "details": "Invalid JWT"
        }

    db = get_db()
    users = db.users

    users_list = users.find({})

    users_coll = []
    for user in users_list:
        users_coll.append({
            "username": user["username"],
            "user_id": str(user["_id"])
        })

    return {
        "status": "Success",
        "users": users_coll
    }
