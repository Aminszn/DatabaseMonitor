
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from dbmonitor.api.app import create_app
from dbmonitor.services.target_monitoring import TargetMonitoringService


def test_create_app_returns_fastapi_application():
    app = create_app()

    assert app.title == "Database Health Monitor"
    assert app.version == "0.1.0"


def test_create_app_registers_target_routes():
    app = create_app()
    paths = app.openapi()["paths"]

    assert "/targets" in paths
    assert "get" in paths["/targets"]
    assert "post" in paths["/targets"]
    assert "/targets/{target_id}/monitor" in paths


def test_create_app_does_not_initialize_database_on_import():
    app = create_app()

    assert app.state.monitoring_engine is None
    assert app.state.targets_repository is None
    assert app.state.metrics_repository is None
    assert app.state.target_monitoring_service is None


def test_application_initializes_monitoring_services(
    monkeypatch,
):
    engine = create_engine("sqlite:///:memory:")

    monkeypatch.setattr(
        "dbmonitor.api.app.create_monitoring_engine",
        lambda settings: engine,
    )

    app = create_app()

    with TestClient(app):
        assert app.state.monitoring_engine is engine
        assert app.state.targets_repository is not None
        assert app.state.metrics_repository is not None
        assert isinstance(
            app.state.target_monitoring_service,
            TargetMonitoringService,
        )

    assert app.state.monitoring_engine is None
    assert app.state.target_monitoring_service is None
