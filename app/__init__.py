from pymongo import MongoClient

from app.config import config


def get_db():
    client = MongoClient(
        f"mongodb+srv://{config.db_user}:{config.db_password}@agstack.oola6."
        f"mongodb.net/{config.db_name}?retryWrites=true&w=majority"
    )
    return client.agstack
