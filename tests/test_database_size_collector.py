
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from dbmonitor.collectors.database_size import DatabaseSizeCollector


@pytest.fixture
def connector():
    return MagicMock()


@pytest.fixture
def collector():
    return DatabaseSizeCollector()


def test_collect_returns_database_size_metric(connector, collector):
    target_id = uuid4()
    connector.get_database_size.return_value = Decimal("8192")

    metric = collector.collect(
        connector=connector,
        target_id=target_id,
        engine="postgresql",
    )

    assert metric.target_id == target_id
    assert metric.engine == "postgresql"
    assert metric.metric_name == "database_size"
    assert metric.value == Decimal("8192")
    assert metric.unit == "bytes"
    connector.get_database_size.assert_called_once()


def test_collect_supports_oracle(connector, collector):
    connector.get_database_size.return_value = Decimal("16384")

    metric = collector.collect(
        connector=connector,
        target_id=uuid4(),
        engine="oracle",
    )

    assert metric.engine == "oracle"
    assert metric.value == Decimal("16384")
    assert metric.unit == "bytes"
