
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


DatabaseEngine = Literal["postgresql", "oracle"]


class Metric(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    target_id: UUID
    engine: DatabaseEngine
    metric_name: str = Field(min_length=1, max_length=100)
    value: Decimal
    unit: str = Field(min_length=1, max_length=30)
    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
