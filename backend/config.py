import secrets

from pydantic import PostgresDsn, BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    API_V1_STR: str
    SECRET_KEY: str = secrets.token_urlsafe(32)

    POOL_SIZE: int = 32
    MAX_OVERFLOW: int = 64
    POSTGRES_PASSWORD: str = "TODO_CHANGE"
    POSTGRES_USER: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = POSTGRES_USER
    DATABASE_URL: PostgresDsn = PostgresDsn(
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}", scheme="postgresql+asyncpg")


    class Config:
        case_sensitive = True
        env_file = "../.env"


settings = Settings()
