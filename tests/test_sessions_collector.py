
from decimal import Decimal
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from dbmonitor.collectors.sessions import SessionCollector


@pytest.fixture
def connector():
    return MagicMock()


@pytest.fixture
def collector():
    return SessionCollector()


def test_collect_returns_active_and_idle_metrics(connector, collector):
    target_id = uuid4()
    connector.get_sessions.return_value = {"active": 4, "idle": 9}

    metrics = collector.collect(
        connector=connector,
        target_id=target_id,
        engine="postgresql",
    )

    assert len(metrics) == 2

    assert metrics[0].target_id == target_id
    assert metrics[0].engine == "postgresql"
    assert metrics[0].metric_name == "sessions_active"
    assert metrics[0].value == Decimal("4")
    assert metrics[0].unit == "sessions"

    assert metrics[1].target_id == target_id
    assert metrics[1].engine == "postgresql"
    assert metrics[1].metric_name == "sessions_idle"
    assert metrics[1].value == Decimal("9")
    assert metrics[1].unit == "sessions"

    connector.get_sessions.assert_called_once()


def test_collect_handles_zero_sessions(connector, collector):
    connector.get_sessions.return_value = {"active": 0, "idle": 0}

    metrics = collector.collect(
        connector=connector,
        target_id=uuid4(),
        engine="oracle",
    )

    assert len(metrics) == 2
    assert all(metric.value == Decimal("0") for metric in metrics)
    assert all(metric.engine == "oracle" for metric in metrics)
