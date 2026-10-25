
from decimal import Decimal
from uuid import UUID

from dbmonitor.connectors.base import BaseConnector
from dbmonitor.models.metrics import DatabaseEngine, Metric


class SessionCollector:
    """Collect active and idle session metrics from a database target."""

    def collect(
        self,
        connector: BaseConnector,
        target_id: UUID,
        engine: DatabaseEngine,
    ) -> list[Metric]:
        """Return metrics for active and idle database sessions."""
        sessions = connector.get_sessions()

        return [
            Metric(
                target_id=target_id,
                engine=engine,
                metric_name=f"sessions_{session_type}",
                value=Decimal(count),
                unit="sessions",
            )
            for session_type, count in sessions.items()
        ]
