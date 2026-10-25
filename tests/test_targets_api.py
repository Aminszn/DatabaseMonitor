
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from dbmonitor.api.targets import router
from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.api.targets import get_targets_repository, router


def make_target() -> DatabaseTarget:
    return DatabaseTarget(
        id=uuid4(),
        name="Development Database",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="development-db",
    )


def create_test_client(repository):
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_targets_repository] = lambda: repository

    return TestClient(app)


def test_create_target_returns_created_target():
    repository = MagicMock()
    target = make_target()
    repository.create_target.return_value = target
    client = create_test_client(repository)

    response = client.post(
        "/targets",
        json={
            "name": target.name,
            "engine": target.engine,
            "host": target.host,
            "port": target.port,
            "database_name": target.database_name,
            "credential_ref": target.credential_ref,
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == target.name
    assert response.json()["id"] == str(target.id)
    assert "credential_ref" not in response.json()
    repository.create_target.assert_called_once()


def test_list_targets_returns_registered_targets():
    repository = MagicMock()
    target = make_target()
    repository.list_targets.return_value = [target]
    client = create_test_client(repository)

    response = client.get("/targets")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == target.name
    assert "credential_ref" not in response.json()


def test_create_target_returns_500_when_repository_fails():
    repository = MagicMock()
    repository.create_target.side_effect = RuntimeError("Database failure")
    client = create_test_client(repository)

    response = client.post(
        "/targets",
        json={
            "name": "Development Database",
            "engine": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database_name": "app_db",
            "credential_ref": "development-db",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to register database target."


def test_create_target_rejects_invalid_request():
    repository = MagicMock()
    client = create_test_client(repository)

    response = client.post(
        "/targets",
        json={
            "name": "Invalid Database",
            "engine": "mysql",
            "host": "localhost",
            "port": 3306,
            "database_name": "app_db",
            "credential_ref": "development-db",
        },
    )

    assert response.status_code == 422
    repository.create_target.assert_not_called()
