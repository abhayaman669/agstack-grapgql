import uvicorn
from fastapi import FastAPI

from app.config import config
from app.routers.authentication import login


app = FastAPI()


app.include_router(login.router, prefix="/login")


if __name__ == '__main__':
    uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
