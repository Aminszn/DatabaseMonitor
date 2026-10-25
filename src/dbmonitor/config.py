
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = "Database Health Monitor"
    environment: str = "development"

    # API settings
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)

    # Monitoring settings
    monitoring_interval_seconds: int = Field(default=60, gt=0)

    # Database connection settings
    monitoring_database_url: SecretStr | None = None
    connect_timeout_seconds: int = Field(default=10, gt=0)
    query_timeout_seconds: int = Field(default=30, gt=0)

    # Logging settings
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
