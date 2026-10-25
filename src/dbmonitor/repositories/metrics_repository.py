
from collections.abc import Sequence

from sqlalchemy import (
    DateTime,
    MetaData,
    Numeric,
    String,
    Table,
    Column,
    Uuid,
    insert,
)
from sqlalchemy.engine import Engine

from dbmonitor.models.metrics import Metric

from uuid import uuid4

metadata = MetaData()

metric_history_table = Table(
    "metric_history",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("target_id", Uuid(as_uuid=True), nullable=False, index=True),
    Column("engine", String(20), nullable=False),
    Column("metric_name", String(100), nullable=False),
    Column("value", Numeric(), nullable=False),
    Column("unit", String(30), nullable=False),
    Column("collected_at", DateTime(timezone=True), nullable=False),
)


class MetricsRepository:
    """Persist collected metrics in the monitoring database."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save_metrics(self, metrics: Sequence[Metric]) -> int:
        """Save metrics and return the number of rows inserted."""
        if not metrics:
            return 0

        records = [
            {
                "id": uuid4(),
                "target_id": metric.target_id,
                "engine": metric.engine,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                "collected_at": metric.collected_at,
            }
            for metric in metrics
        ]

        with self._engine.begin() as connection:
            connection.execute(insert(metric_history_table), records)

        return len(records)
