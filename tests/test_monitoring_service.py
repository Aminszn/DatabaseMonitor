
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from dbmonitor.services.monitoring import MonitoringService


@pytest.fixture
def connector():
    mock_connector = MagicMock()
    mock_connector.check_health.return_value = True
    mock_connector.get_sessions.return_value = {
        "active": 3,
        "idle": 7,
    }
    mock_connector.get_database_size.return_value = Decimal("8192")
    return mock_connector


@pytest.fixture
def service():
    return MonitoringService()


def test_collect_metrics_returns_all_four_metrics(connector, service):
    target_id = uuid4()

    metrics = service.collect_metrics(
        connector=connector,
        target_id=target_id,
        engine="postgresql",
    )

    assert len(metrics) == 4
    assert [metric.metric_name for metric in metrics] == [
        "health_status",
        "sessions_active",
        "sessions_idle",
        "database_size",
    ]
    assert all(metric.target_id == target_id for metric in metrics)
    assert all(metric.engine == "postgresql" for metric in metrics)

    connector.check_health.assert_called_once()
    connector.get_sessions.assert_called_once()
    connector.get_database_size.assert_called_once()


def test_collect_metrics_supports_oracle(connector, service):
    metrics = service.collect_metrics(
        connector=connector,
        target_id=uuid4(),
        engine="oracle",
    )

    assert len(metrics) == 4
    assert all(metric.engine == "oracle" for metric in metrics)


def test_collect_metrics_preserves_unhealthy_status(connector, service):
    connector.check_health.return_value = False

    metrics = service.collect_metrics(
        connector=connector,
        target_id=uuid4(),
        engine="postgresql",
    )

    health_metric = next(
        metric for metric in metrics
        if metric.metric_name == "health_status"
    )

    assert health_metric.value == Decimal("0")
