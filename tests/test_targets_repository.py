
from uuid import uuid4

import pytest
from sqlalchemy import create_engine

from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.repositories.metrics_repository import metadata
from dbmonitor.repositories.targets_repository import TargetsRepository


@pytest.fixture
def database_engine():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture
def repository(database_engine):
    return TargetsRepository(database_engine)


@pytest.fixture
def target():
    return DatabaseTarget(
        id=uuid4(),
        name="Development Database",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="development-db",
    )


def test_create_target(repository, target):
    created = repository.create_target(target)

    assert created == target


def test_get_target_returns_existing_target(repository, target):
    repository.create_target(target)

    retrieved = repository.get_target(target.id)

    assert retrieved == target


def test_get_target_returns_none_for_missing_id(repository):
    assert repository.get_target(uuid4()) is None


def test_list_targets_returns_targets_sorted_by_name(
    repository,
    database_engine,
):
    second = DatabaseTarget(
        id=uuid4(),
        name="Production",
        engine="oracle",
        host="db.example.com",
        port=1521,
        database_name="ORCL",
        credential_ref="production-db",
    )
    first = DatabaseTarget(
        id=uuid4(),
        name="Development",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="development-db",
    )

    repository.create_target(second)
    repository.create_target(first)

    targets = repository.list_targets()

    assert [item.name for item in targets] == [
        "Development",
        "Production",
    ]


def test_create_target_preserves_disabled_status(repository):
    target = DatabaseTarget(
        id=uuid4(),
        name="Disabled Database",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="disabled-db",
        enabled=False,
    )

    repository.create_target(target)

    retrieved = repository.get_target(target.id)

    assert retrieved is not None
    assert retrieved.enabled is False
