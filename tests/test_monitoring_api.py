
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from dbmonitor.api.targets import (
    get_target_monitoring_service,
    router,
)
from dbmonitor.models.metrics import Metric
from dbmonitor.services.target_monitoring import TargetMonitoringService

def create_test_client(service):
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_target_monitoring_service] = (
        lambda: service
    )

    return TestClient(app)


def test_monitor_target_returns_collected_metrics():
    service = MagicMock()
    target_id = uuid4()

    service.monitor_target.return_value = [
        Metric(
            target_id=target_id,
            engine="postgresql",
            metric_name="health_status",
            value=Decimal("1"),
            unit="status",
        )
    ]

    client = create_test_client(service)
    response = client.post(f"/targets/{target_id}/monitor")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["metric_name"] == "health_status"
    assert response.json()[0]["value"] == "1"
    service.monitor_target.assert_called_once_with(target_id)


def test_monitor_target_returns_404_when_target_is_missing():
    service = MagicMock()
    target_id = uuid4()
    service.monitor_target.side_effect = LookupError("Target not found")

    client = create_test_client(service)
    response = client.post(f"/targets/{target_id}/monitor")

    assert response.status_code == 404
    assert response.json()["detail"] == "Database target was not found."


def test_monitor_target_returns_409_when_target_cannot_be_monitored():
    service = MagicMock()
    target_id = uuid4()
    service.monitor_target.side_effect = ValueError("Target is disabled")

    client = create_test_client(service)
    response = client.post(f"/targets/{target_id}/monitor")

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Database target cannot be monitored."
    )


def test_monitor_target_returns_500_when_monitoring_fails():
    service = MagicMock()
    target_id = uuid4()
    service.monitor_target.side_effect = RuntimeError("Internal failure")

    client = create_test_client(service)
    response = client.post(f"/targets/{target_id}/monitor")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Failed to monitor database target."
    )


def test_monitor_target_rejects_invalid_target_id():
    service = MagicMock()
    client = create_test_client(service)

    response = client.post("/targets/not-a-uuid/monitor")

    assert response.status_code == 422
    service.monitor_target.assert_not_called()
