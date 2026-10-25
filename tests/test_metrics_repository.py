
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select

from dbmonitor.models.metrics import Metric
from dbmonitor.repositories.metrics_repository import (
    MetricsRepository,
    metadata,
    metric_history_table,
)


@pytest.fixture
def database_engine():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture
def repository(database_engine):
    return MetricsRepository(database_engine)


def test_save_metrics_persists_records(repository, database_engine):
    target_id = uuid4()
    collected_at = datetime.now(timezone.utc)

    metrics = [
        Metric(
            target_id=target_id,
            engine="postgresql",
            metric_name="health_status",
            value=Decimal("1"),
            unit="status",
            collected_at=collected_at,
        ),
        Metric(
            target_id=target_id,
            engine="postgresql",
            metric_name="sessions_active",
            value=Decimal("4"),
            unit="sessions",
            collected_at=collected_at,
        ),
    ]

    inserted = repository.save_metrics(metrics)

    assert inserted == 2

    with database_engine.connect() as connection:
        rows = connection.execute(
            select(metric_history_table).order_by(
                metric_history_table.c.metric_name
            )
        ).mappings().all()

    assert len(rows) == 2
    assert rows[0]["target_id"] == target_id
    assert rows[0]["engine"] == "postgresql"
    assert rows[0]["metric_name"] == "health_status"
    assert rows[0]["value"] == Decimal("1")
    assert rows[0]["unit"] == "status"
    assert rows[1]["metric_name"] == "sessions_active"
    assert rows[1]["value"] == Decimal("4")


def test_save_metrics_returns_zero_for_empty_input(repository):
    assert repository.save_metrics([]) == 0


def test_save_metrics_supports_oracle(repository, database_engine):
    metric = Metric(
        target_id=uuid4(),
        engine="oracle",
        metric_name="database_size",
        value=Decimal("8192"),
        unit="bytes",
    )

    assert repository.save_metrics([metric]) == 1

    with database_engine.connect() as connection:
        row = connection.execute(
            select(metric_history_table).where(
                metric_history_table.c.engine == "oracle"
            )
        ).mappings().one()

    assert row["engine"] == "oracle"
    assert row["metric_name"] == "database_size"
    assert row["value"] == Decimal("8192")
