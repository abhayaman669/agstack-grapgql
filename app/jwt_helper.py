import jwt
from bson.objectid import ObjectId

from app import get_db
from app.config import config


def verify_jwt(jwt_code):
    try:
        return jwt.decode(jwt_code, key=config.jwt_secret_key)
    except Exception as e:
        print(e)
        return None


def user_exists(user_id):

    db = get_db()
    users = db.users

    user = users.find_one({
        '_id': ObjectId(user_id)
    })

    return user
