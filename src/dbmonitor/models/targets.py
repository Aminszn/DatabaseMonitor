
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatabaseTarget(BaseModel):
    """Configuration for a database monitored by the application."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    id: UUID
    name: str = Field(min_length=1, max_length=100)
    engine: Literal["postgresql", "oracle"]
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    database_name: str = Field(min_length=1, max_length=255)
    credential_ref: str = Field(min_length=1, max_length=255)
    enabled: bool = True
