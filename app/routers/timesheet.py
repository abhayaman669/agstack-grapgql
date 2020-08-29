from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from app import get_db
from app.jwt_helper import verify_jwt, user_exists


router = APIRouter()


class TimeData(BaseModel):
    user_id: str
    timestamp: str
    event: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/")
async def timesheet_events(
        time_data: TimeData, token: str = Depends(oauth2_scheme)):
    # verifing JWT
    jwt_data = verify_jwt(token)
    if not jwt_data:
        return {
            "status": "Failed",
            "details": "Invalid JWT"
        }

    # Getting todays date
    today_date = datetime.now().date()

    # Init collections
    db = get_db()
    timesheets = db.timesheets

    # Check if the user exists
    user = user_exists(time_data.user_id)
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
    timesheet = timesheets.find_one(query)

    # If there is no doc for today then create one
    if not timesheet:
        timesheet = {
            **query,
            "status": "INACTIVE"
        }

        timesheets.insert(timesheet)
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
        timesheets.update_one(
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
        timesheets.update_one(
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
        timesheets.update_one(
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
        timesheets.update_one(
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
