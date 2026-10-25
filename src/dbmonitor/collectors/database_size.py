
from uuid import UUID

from dbmonitor.connectors.base import BaseConnector
from dbmonitor.models.metrics import DatabaseEngine, Metric


class DatabaseSizeCollector:
    """Collect allocated database size in bytes."""

    def collect(
        self,
        connector: BaseConnector,
        target_id: UUID,
        engine: DatabaseEngine,
    ) -> Metric:
        """Return the database-size metric for a target."""
        size_bytes = connector.get_database_size()

        return Metric(
            target_id=target_id,
            engine=engine,
            metric_name="database_size",
            value=size_bytes,
            unit="bytes",
        )
