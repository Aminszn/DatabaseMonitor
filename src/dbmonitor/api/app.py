
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dbmonitor.api.targets import (
    get_target_monitoring_service,
    get_targets_repository,
    router,
)
from dbmonitor.config import get_settings
from dbmonitor.connectors.factory import ConnectorFactory
from dbmonitor.database import create_monitoring_engine
from dbmonitor.repositories.metrics_repository import MetricsRepository
from dbmonitor.repositories.targets_repository import TargetsRepository
from dbmonitor.services.monitoring import MonitoringService
from dbmonitor.services.target_monitoring import TargetMonitoringService


def create_app() -> FastAPI:
    """Create and configure the Database Monitor API."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Initialize and release application resources."""
        settings = get_settings()
        engine = create_monitoring_engine(settings)

        app.state.monitoring_engine = engine
        app.state.targets_repository = TargetsRepository(engine)
        app.state.metrics_repository = MetricsRepository(engine)

        app.state.target_monitoring_service = TargetMonitoringService(
            targets_repository=app.state.targets_repository,
            connector_factory=ConnectorFactory(
                connect_timeout_seconds=settings.connect_timeout_seconds,
            ),
            monitoring_service=MonitoringService(),
            metrics_repository=app.state.metrics_repository,
        )

        try:
            yield
        finally:
            engine.dispose()
            app.state.monitoring_engine = None
            app.state.targets_repository = None
            app.state.metrics_repository = None
            app.state.target_monitoring_service = None

    app = FastAPI(
        title="Database Health Monitor",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.monitoring_engine = None
    app.state.targets_repository = None
    app.state.metrics_repository = None
    app.state.target_monitoring_service = None

    def provide_targets_repository() -> TargetsRepository:
        repository = app.state.targets_repository

        if repository is None:
            raise RuntimeError(
                "Monitoring database is not initialized."
            )

        return repository

    def provide_target_monitoring_service() -> TargetMonitoringService:
        service = app.state.target_monitoring_service

        if service is None:
            raise RuntimeError(
                "Target monitoring service is not initialized."
            )

        return service

    app.dependency_overrides[get_targets_repository] = (
        provide_targets_repository
    )
    app.dependency_overrides[get_target_monitoring_service] = (
        provide_target_monitoring_service
    )

    app.include_router(router)

    return app
