
import logging

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from dbmonitor.api.schemas import TargetCreate, TargetResponse
from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.repositories.targets_repository import TargetsRepository
from dbmonitor.models.metrics import Metric
from dbmonitor.services.target_monitoring import TargetMonitoringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/targets", tags=["Targets"])


def get_targets_repository() -> TargetsRepository:
    """Provide the target repository to API endpoints."""
    raise RuntimeError("Target repository dependency is not configured.")


@router.post(
    "",
    response_model=TargetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_target(
    payload: TargetCreate,
    repository: TargetsRepository = Depends(get_targets_repository),
) -> TargetResponse:
    """Register a database target."""
    target = DatabaseTarget(
        id=uuid4(),
        **payload.model_dump(),
    )

    try:
        created_target = repository.create_target(target)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register database target.",
        ) from exc

    return TargetResponse(
        id=created_target.id,
        name=created_target.name,
        engine=created_target.engine,
        host=created_target.host,
        port=created_target.port,
        database_name=created_target.database_name,
        enabled=created_target.enabled,
    )


@router.get("", response_model=list[TargetResponse])
def list_targets(
    repository: TargetsRepository = Depends(get_targets_repository),
) -> list[TargetResponse]:
    """Return all registered database targets."""
    targets = repository.list_targets()

    return [
        TargetResponse(
            id=target.id,
            name=target.name,
            engine=target.engine,
            host=target.host,
            port=target.port,
            database_name=target.database_name,
            enabled=target.enabled,
        )
        for target in targets
    ]


def get_target_monitoring_service() -> TargetMonitoringService:
    """Provide the target monitoring service to API endpoints."""
    raise RuntimeError(
        "Target monitoring service dependency is not configured."
    )


@router.post(
    "/{target_id}/monitor",
    response_model=list[Metric],
)

def monitor_target(
    target_id: UUID,
    service: TargetMonitoringService = Depends(
        get_target_monitoring_service
    ),
) -> list[Metric]:
    """Collect and persist metrics for a registered database target."""
    try:
        return service.monitor_target(target_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database target was not found.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database target cannot be monitored.",
        ) from exc
    except Exception as exc:
        logger.exception(
            "Failed to monitor database target %s",
            target_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to monitor database target.",
        ) from exc
