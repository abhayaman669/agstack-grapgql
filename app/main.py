import uvicorn
from fastapi import FastAPI

from app.config import config
from app.routers.authentication import login, signup
from app.routers import timesheet, users, profile, inks, papers
from app.db.mongodb_utils import connect_to_mongo, close_mongo_connection


app = FastAPI()

# connecting and closing
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# Routes
app.include_router(login.router, prefix="/login")
app.include_router(signup.router, prefix="/signup")

app.include_router(timesheet.router, prefix="/timesheet")

app.include_router(users.router, prefix="/users")

app.include_router(profile.router, prefix="/profile")

app.include_router(inks.router, prefix="/inks")

app.include_router(papers.router, prefix="/papers")


if __name__ == '__main__':
    uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
