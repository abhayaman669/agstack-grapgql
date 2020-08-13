import uvicorn
from fastapi import FastAPI

from app.config import config


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == '__main__':
    uvicorn.run("main:app", host=config.host, port=config.port, reload=True)
