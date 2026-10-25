
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from dbmonitor.config import Settings, get_settings


def create_monitoring_engine(
    settings: Settings | None = None,
) -> Engine:
    """Create the SQLAlchemy engine for the monitoring database."""
    if settings is None:
        settings = get_settings()

    database_url = settings.monitoring_database_url

    if database_url is None:
        raise RuntimeError(
            "MONITORING_DATABASE_URL must be configured."
        )

    return create_engine(
        database_url.get_secret_value(),
        pool_pre_ping=True,
    )
