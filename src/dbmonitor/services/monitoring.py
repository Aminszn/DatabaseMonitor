
from uuid import UUID

from dbmonitor.collectors.database_size import DatabaseSizeCollector
from dbmonitor.collectors.health import HealthCollector
from dbmonitor.collectors.sessions import SessionCollector
from dbmonitor.connectors.base import BaseConnector
from dbmonitor.models.metrics import DatabaseEngine, Metric


class MonitoringService:
    """Coordinate metric collection for a database target."""

    def __init__(self) -> None:
        self._health_collector = HealthCollector()
        self._session_collector = SessionCollector()
        self._database_size_collector = DatabaseSizeCollector()

    def collect_metrics(
        self,
        connector: BaseConnector,
        target_id: UUID,
        engine: DatabaseEngine,
    ) -> list[Metric]:
        """Collect all supported metrics for one database target."""
        metrics = [
            self._health_collector.collect(
                connector=connector,
                target_id=target_id,
                engine=engine,
            )
        ]

        metrics.extend(
            self._session_collector.collect(
                connector=connector,
                target_id=target_id,
                engine=engine,
            )
        )

        metrics.append(
            self._database_size_collector.collect(
                connector=connector,
                target_id=target_id,
                engine=engine,
            )
        )

        return metrics
