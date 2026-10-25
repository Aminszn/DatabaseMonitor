
from decimal import Decimal
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from dbmonitor.collectors.health import HealthCollector


@pytest.fixture
def connector():
    return MagicMock()


@pytest.fixture
def collector():
    return HealthCollector()


def test_collect_returns_healthy_metric(connector, collector):
    target_id = uuid4()
    connector.check_health.return_value = True

    metric = collector.collect(
        connector=connector,
        target_id=target_id,
        engine="postgresql",
    )

    assert metric.target_id == target_id
    assert metric.engine == "postgresql"
    assert metric.metric_name == "health_status"
    assert metric.value == Decimal("1")
    assert metric.unit == "status"
    connector.check_health.assert_called_once()


def test_collect_returns_unhealthy_metric(connector, collector):
    target_id = uuid4()
    connector.check_health.return_value = False

    metric = collector.collect(
        connector=connector,
        target_id=target_id,
        engine="oracle",
    )

    assert metric.target_id == target_id
    assert metric.engine == "oracle"
    assert metric.metric_name == "health_status"
    assert metric.value == Decimal("0")
    assert metric.unit == "status"
    connector.check_health.assert_called_once()
