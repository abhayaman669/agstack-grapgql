from pydantic import BaseModel
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import config
from app.helpers.jwt_helper import verify_jwt
from app.db.mongodb import get_database, AsyncIOMotorClient


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class InkData(BaseModel):
    company_name: str
    ink_name: str
    color: str
    color_hex: str = None


@router.post("/")
async def timesheet_events(
    ink_data: InkData,
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

    if jwt_data["user_type"] != "admin":
        return {
            "status": "Failed",
            "details": "You are not allowed to add ink."
        }

    data = dict(
        company_name=ink_data.company_name,
        ink_name=ink_data.ink_name,
        color=ink_data.color,
        color_hex=ink_data.color_hex
    )

    await db[config.db_name][config.inks_collc_name].insert_one(
        data
    )

    return {
        "status": "Success",
        "detail": "Ink added Successfully"
    }
