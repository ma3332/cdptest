from pydantic import BaseSettings


# Capital Insensitive is also a plus point of this pydantic lib for setting environment parameters


class Settings(BaseSettings):
    database_host: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"


setting = Settings()
