
from decimal import Decimal
from uuid import UUID

from dbmonitor.connectors.base import BaseConnector
from dbmonitor.models.metrics import DatabaseEngine, Metric


class HealthCollector:
    """Collect a health-status metric from a database target."""

    def collect(
        self,
        connector: BaseConnector,
        target_id: UUID,
        engine: DatabaseEngine,
    ) -> Metric:
        """Return a metric indicating whether the target is healthy."""
        is_healthy = connector.check_health()

        return Metric(
            target_id=target_id,
            engine=engine,
            metric_name="health_status",
            value=Decimal("1") if is_healthy else Decimal("0"),
            unit="status",
        )
