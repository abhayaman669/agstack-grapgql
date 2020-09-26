from pydantic import BaseSettings


class Config(BaseSettings):

    host: str = "localhost"
    port: int = 8000
    db_user: str
    db_password: str
    db_name: str
    token: str
    jwt_secret_key: str
    user_collection_name: str = "users"
    timesheet_collc_name: str = "timesheets"
    inks_collc_name: str = "inks"
    papers_collc_name: str = "papers"


config = Config()
