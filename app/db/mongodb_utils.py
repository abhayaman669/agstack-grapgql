from motor.motor_asyncio import AsyncIOMotorClient

from app.config import config
from app.db.mongodb import db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(
        f"mongodb+srv://{config.db_user}:{config.db_password}@agstack.oola6."
        f"mongodb.net/{config.db_name}?retryWrites=true&w=majority"
    )


async def close_mongo_connection():
    db.client.close()
