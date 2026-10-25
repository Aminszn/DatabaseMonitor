
from uuid import UUID

from sqlalchemy import Boolean, Column, Integer, String, Uuid, insert, select
from sqlalchemy.engine import Engine

from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.repositories.metrics_repository import metadata


database_targets_table = metadata.tables.get("database_targets")

if database_targets_table is None:
    from sqlalchemy import Table

    database_targets_table = Table(
        "database_targets",
        metadata,
        Column("id", Uuid(as_uuid=True), primary_key=True),
        Column("name", String(100), nullable=False),
        Column("engine", String(20), nullable=False),
        Column("host", String(255), nullable=False),
        Column("port", Integer, nullable=False),
        Column("database_name", String(255), nullable=False),
        Column("credential_ref", String(255), nullable=False),
        Column(
            "enabled",
            Boolean,
            nullable=False,
            server_default="1",
        ),
    )


class TargetsRepository:
    """Persist and retrieve monitored database targets."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def create_target(self, target: DatabaseTarget) -> DatabaseTarget:
        """Insert a target and return the created target."""
        record = target.model_dump()

        with self._engine.begin() as connection:
            connection.execute(
                insert(database_targets_table).values(**record)
            )

        return target

    def get_target(self, target_id: UUID) -> DatabaseTarget | None:
        """Return a target by ID, or None if it does not exist."""
        query = select(database_targets_table).where(
            database_targets_table.c.id == target_id
        )

        with self._engine.connect() as connection:
            row = connection.execute(query).mappings().first()

        if row is None:
            return None

        return DatabaseTarget.model_validate(dict(row))

    def list_targets(self) -> list[DatabaseTarget]:
        """Return all configured targets."""
        query = select(database_targets_table).order_by(
            database_targets_table.c.name
        )

        with self._engine.connect() as connection:
            rows = connection.execute(query).mappings().all()

        return [
            DatabaseTarget.model_validate(dict(row))
            for row in rows
        ]
