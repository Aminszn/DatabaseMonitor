
from uuid import UUID

from dbmonitor.connectors.factory import ConnectorFactory
from dbmonitor.models.metrics import Metric
from dbmonitor.repositories.metrics_repository import MetricsRepository
from dbmonitor.repositories.targets_repository import TargetsRepository
from dbmonitor.services.monitoring import MonitoringService


class TargetMonitoringService:
    """Coordinate metric collection and persistence for one target."""

    def __init__(
        self,
        targets_repository: TargetsRepository,
        connector_factory: ConnectorFactory,
        monitoring_service: MonitoringService,
        metrics_repository: MetricsRepository,
    ) -> None:
        self._targets_repository = targets_repository
        self._connector_factory = connector_factory
        self._monitoring_service = monitoring_service
        self._metrics_repository = metrics_repository

    def monitor_target(self, target_id: UUID) -> list[Metric]:
        """Collect and persist metrics for an enabled target."""
        target = self._targets_repository.get_target(target_id)

        if target is None:
            raise LookupError(f"Database target '{target_id}' was not found.")

        if not target.enabled:
            raise ValueError(f"Database target '{target_id}' is disabled.")

        connector = self._connector_factory.create(target)

        try:
            metrics = self._monitoring_service.collect_metrics(
                connector=connector,
                target_id=target.id,
                engine=target.engine,
            )

            self._metrics_repository.save_metrics(metrics)

            return metrics
        finally:
            connector.close()
