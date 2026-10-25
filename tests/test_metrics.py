
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from dbmonitor.models.metrics import Metric


def test_metric_creation():
    target_id = uuid4()

    metric = Metric(
        target_id=target_id,
        engine="postgresql",
        metric_name="active_sessions",
        value=Decimal("12"),
        unit="sessions",
    )

    assert metric.target_id == target_id
    assert metric.engine == "postgresql"
    assert metric.metric_name == "active_sessions"
    assert metric.value == Decimal("12")
    assert metric.unit == "sessions"
    assert metric.collected_at.tzinfo is not None


def test_metric_accepts_oracle_engine():
    metric = Metric(
        target_id=uuid4(),
        engine="oracle",
        metric_name="database_size",
        value=Decimal("1024"),
        unit="bytes",
    )

    assert metric.engine == "oracle"


def test_metric_rejects_unsupported_engine():
    with pytest.raises(ValidationError):
        Metric(
            target_id=uuid4(),
            engine="mysql",
            metric_name="active_sessions",
            value=Decimal("12"),
            unit="sessions",
        )


def test_metric_rejects_empty_metric_name():
    with pytest.raises(ValidationError):
        Metric(
            target_id=uuid4(),
            engine="postgresql",
            metric_name="",
            value=Decimal("12"),
            unit="sessions",
        )


def test_metric_is_immutable():
    metric = Metric(
        target_id=uuid4(),
        engine="postgresql",
        metric_name="active_sessions",
        value=Decimal("12"),
        unit="sessions",
    )

    with pytest.raises(ValidationError):
        metric.value = Decimal("20")


def test_metric_accepts_timezone_aware_timestamp():
    timestamp = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)

    metric = Metric(
        target_id=uuid4(),
        engine="postgresql",
        metric_name="response_time",
        value=Decimal("15.5"),
        unit="milliseconds",
        collected_at=timestamp,
    )

    assert metric.collected_at == timestamp
