
import pytest
from sqlalchemy.engine import Engine

from dbmonitor.config import Settings
from dbmonitor.database import create_monitoring_engine


def test_create_monitoring_engine_returns_engine():
    settings = Settings(
        monitoring_database_url="sqlite+pysqlite:///:memory:"
    )

    engine = create_monitoring_engine(settings)

    try:
        assert isinstance(engine, Engine)
        assert engine.dialect.name == "sqlite"
        assert engine.pool._pre_ping is True
    finally:
        engine.dispose()


def test_create_monitoring_engine_requires_database_url():
    settings = Settings(monitoring_database_url=None)

    with pytest.raises(
        RuntimeError,
        match="MONITORING_DATABASE_URL must be configured",
    ):
        create_monitoring_engine(settings)
