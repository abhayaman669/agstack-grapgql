import uvicorn
from fastapi import FastAPI

from app.config import config
from app.routers.authentication import login, signup
from app.routers import timesheet, users


app = FastAPI()


app.include_router(login.router, prefix="/login")
app.include_router(signup.router, prefix="/signup")

app.include_router(timesheet.router, prefix="/timesheet")

app.include_router(users.router, prefix="/users")


if __name__ == '__main__':
    uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
