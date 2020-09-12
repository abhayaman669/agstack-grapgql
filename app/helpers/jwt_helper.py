import jwt

from app.config import config


def verify_jwt(jwt_code):
    try:
        return jwt.decode(jwt_code, key=config.jwt_secret_key)
    except Exception as e:
        print(e)
        return None
