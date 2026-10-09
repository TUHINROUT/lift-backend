from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings
    """

    APP_NAME: str = "Lift Service API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    API_PREFIX: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DATABASE_URL: str

    LOG_LEVEL: str

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    DEFAULT_FROM_EMAIL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns cached application settings.
    """
    return Settings()


settings = get_settings()