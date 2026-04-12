from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment and optional `.env` file."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/db.sqlite3"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
