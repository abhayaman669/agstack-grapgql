from pydantic import BaseSettings


class Config(BaseSettings):

    host: str = "localhost"
    port: int = 8000
    db_user: str
    db_password: str
    db_name: str


config = Config()
