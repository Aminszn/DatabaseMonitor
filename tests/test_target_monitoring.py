
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from dbmonitor.models.metrics import Metric
from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.services.target_monitoring import TargetMonitoringService


@pytest.fixture
def target():
    return DatabaseTarget(
        id=uuid4(),
        name="Development Database",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="development-db",
    )


@pytest.fixture
def dependencies(target):
    targets_repository = MagicMock()
    targets_repository.get_target.return_value = target

    connector = MagicMock()
    connector_factory = MagicMock()
    connector_factory.create.return_value = connector

    metrics = [
        Metric(
            target_id=target.id,
            engine="postgresql",
            metric_name="health_status",
            value=Decimal("1"),
            unit="status",
        )
    ]

    monitoring_service = MagicMock()
    monitoring_service.collect_metrics.return_value = metrics

    metrics_repository = MagicMock()

    service = TargetMonitoringService(
        targets_repository=targets_repository,
        connector_factory=connector_factory,
        monitoring_service=monitoring_service,
        metrics_repository=metrics_repository,
    )

    return {
        "service": service,
        "targets_repository": targets_repository,
        "connector_factory": connector_factory,
        "connector": connector,
        "monitoring_service": monitoring_service,
        "metrics_repository": metrics_repository,
        "metrics": metrics,
    }


def test_monitor_target_collects_and_persists_metrics(dependencies, target):
    result = dependencies["service"].monitor_target(target.id)

    assert result == dependencies["metrics"]

    dependencies["targets_repository"].get_target.assert_called_once_with(
        target.id
    )
    dependencies["connector_factory"].create.assert_called_once_with(target)
    dependencies["monitoring_service"].collect_metrics.assert_called_once_with(
        connector=dependencies["connector"],
        target_id=target.id,
        engine="postgresql",
    )
    dependencies["metrics_repository"].save_metrics.assert_called_once_with(
        dependencies["metrics"]
    )
    dependencies["connector"].close.assert_called_once()


def test_monitor_target_rejects_missing_target(dependencies):
    target_id = uuid4()
    dependencies["targets_repository"].get_target.return_value = None

    with pytest.raises(LookupError, match="was not found"):
        dependencies["service"].monitor_target(target_id)

    dependencies["connector_factory"].create.assert_not_called()


def test_monitor_target_rejects_disabled_target(dependencies, target):
    disabled_target = target.model_copy(update={"enabled": False})
    dependencies["targets_repository"].get_target.return_value = disabled_target

    with pytest.raises(ValueError, match="is disabled"):
        dependencies["service"].monitor_target(target.id)

    dependencies["connector_factory"].create.assert_not_called()


def test_monitor_target_closes_connector_when_collection_fails(
    dependencies,
    target,
):
    dependencies["monitoring_service"].collect_metrics.side_effect = (
        RuntimeError("Collection failed")
    )

    with pytest.raises(RuntimeError, match="Collection failed"):
        dependencies["service"].monitor_target(target.id)

    dependencies["metrics_repository"].save_metrics.assert_not_called()
    dependencies["connector"].close.assert_called_once()


def test_monitor_target_closes_connector_when_persistence_fails(
    dependencies,
    target,
):
    dependencies["metrics_repository"].save_metrics.side_effect = (
        RuntimeError("Persistence failed")
    )

    with pytest.raises(RuntimeError, match="Persistence failed"):
        dependencies["service"].monitor_target(target.id)

    dependencies["connector"].close.assert_called_once()
