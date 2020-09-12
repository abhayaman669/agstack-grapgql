from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from app.config import config
from app.helpers.jwt_helper import verify_jwt
from app.db.mongodb import get_database, AsyncIOMotorClient
from app.helpers.users_helper import check_user_with_user_id


router = APIRouter()


class TimeData(BaseModel):
    user_id: str
    timestamp: str
    event: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/")
async def timesheet_events(
        time_data: TimeData,
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

    # Getting todays date
    today_date = datetime.now().date()

    # Check if the user exists
    user = await check_user_with_user_id(db, time_data.user_id)

    if not user:
        return {
            "status": "Failed",
            "details": "User not Found."
        }

    # Getting todays timesheet
    query = {
        "user_id": time_data.user_id,
        "date": str(today_date)
    }

    timesheet = await db[config.db_name][config.timesheet_collc_name].find_one(
        query
    )

    # If there is no doc for today then create one
    if not timesheet:
        timesheet = {
            **query,
            "status": "INACTIVE"
        }

        await db[config.db_name][config.timesheet_collc_name].insert_one(
            timesheet
        )
    elif timesheet["status"] == "STOPPED":
        return {
            "status": "Success",
            "detail": timesheet["status"]
        }

    # Process according to event
    if time_data.event == "STATUS":
        return {
            "status": "Success",
            "detail": timesheet["status"]
        }
    elif time_data.event == "START":
        # If the timesheet is already started
        if timesheet["status"] != "INACTIVE":
            return {
                "status": "Failed",
                "detail": "Time has already started."
            }

        # Update doc
        await db[config.db_name][config.timesheet_collc_name].update_one(
            query,
            {
                "$set": {
                    "in_time": time_data.timestamp,
                    "status": "ACTIVE"
                }
            }
        )

        return {
            "status": "Success",
            "detail": "Started time for today."
        }
    elif time_data.event == "PAUSE":
        # If the time is not started then show error
        if timesheet["status"] != "ACTIVE":
            return {
                "status": "Failed",
                "detail": "Please start or continue the time first."
            }

        breaks = {}
        if "breaks" in timesheet:
            breaks = timesheet["breaks"]

        index = str(len(breaks) + 1)
        breaks[index] = {
            "from": time_data.timestamp
        }

        # Update doc
        await db[config.db_name][config.timesheet_collc_name].update_one(
            query,
            {
                "$set": {
                    "breaks": breaks,
                    "status": "PAUSED"
                }
            }
        )

        return {
            "status": "Success",
            "detail": "Paused timer."
        }
    elif time_data.event == "CONTINUE":
        # If the time is not started then show error
        if timesheet["status"] != "PAUSED":
            return {
                "status": "Failed",
                "detail": "Please pause the time first."
            }

        breaks = timesheet["breaks"]

        index = str(len(breaks))
        breaks[index]["to"] = time_data.timestamp

        # Update doc
        await db[config.db_name][config.timesheet_collc_name].update_one(
            query,
            {
                "$set": {
                    "breaks": breaks,
                    "status": "ACTIVE"
                }
            }
        )

        return {
            "status": "Success",
            "detail": "Timer continued."
        }
    elif time_data.event == "STOP":
        # If the time is not started then show error
        if timesheet["status"] != "ACTIVE":
            return {
                "status": "Failed",
                "detail": "Please start the timer first."
            }

        # Update doc
        await db[config.db_name][config.timesheet_collc_name].update_one(
            query,
            {
                "$set": {
                    "out_time": time_data.timestamp,
                    "status": "STOPPED"
                }
            }
        )
        return {
            "status": "Success",
            "detail": "Timer stopped."
        }
    else:
        return {
            "status": "Failed",
            "detail": "Invalid event"
        }
