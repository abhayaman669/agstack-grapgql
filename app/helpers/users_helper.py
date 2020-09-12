from uuid import uuid4

import jwt
import bcrypt
from bson import ObjectId

from app.config import config
from app.db.mongodb import AsyncIOMotorClient


async def get_authorize_user_jwt(conn: AsyncIOMotorClient, username, password):
    user = await conn[config.db_name][config.user_collection_name].find_one(
        {"username": username}
    )

    if not user:
        return {
            "status": "Failed",
            "detail": "User not found with this username."
        }

    if not bcrypt.checkpw(password, user["password"]):
        return {
            "status": "Failed",
            "detail": "Invalid password."
        }

    # Generating access_token
    access_token = jwt.encode(
            {
                "user_id": str(user["_id"]),
                "username": user["username"]
            },
            key=config.jwt_secret_key
    ).decode("utf-8")

    return {
        "status": "Success",
        "access_token": access_token
    }


async def check_user_with_email(
    conn: AsyncIOMotorClient, email
):
    user = await conn[config.db_name][config.user_collection_name].find_one(
        {"email": email}
    )

    if user:
        return True
    else:
        return False


async def check_user_with_username(
    conn: AsyncIOMotorClient, username
):
    user = await conn[config.db_name][config.user_collection_name].find_one(
        {"username": username}
    )

    if user:
        return True
    else:
        return False


async def check_user_with_user_id(
    conn: AsyncIOMotorClient, user_id
):

    user = await conn[config.db_name][config.user_collection_name].find_one(
        {"_id": ObjectId(user_id)}
    )

    if user:
        user["_id"] = str(user["_id"])

        return user
    return None


async def create_new_user(
        conn: AsyncIOMotorClient,
        first_name,
        last_name,
        phone,
        user_type,
        username,
        email,
        password_hash
):

    data = dict(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        user_type=user_type,
        username=username,
        email=email,
        password=password_hash
    )

    await conn[config.db_name][config.user_collection_name].insert_one(
        data
    )
