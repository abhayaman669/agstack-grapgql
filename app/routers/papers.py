from pydantic import BaseModel
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import config
from app.helpers.jwt_helper import verify_jwt
from app.db.mongodb import get_database, AsyncIOMotorClient


router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class PaperData(BaseModel):
    company_name: str
    paper_type: str = None
    paper_size: int = None
    paper_gsm: int = None


@router.post("/")
async def timesheet_events(
    paper_data: PaperData,
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
            "details": "You are not allowed to add paper."
        }

    data = dict(
        company_name=paper_data.company_name,
        paper_type=paper_data.paper_type,
        paper_size=paper_data.paper_size,
        paper_gsm=paper_data.paper_gsm
    )

    await db[config.db_name][config.papers_collc_name].insert_one(
        data
    )

    return {
        "status": "Success",
        "detail": "paper added Successfully"
    }
