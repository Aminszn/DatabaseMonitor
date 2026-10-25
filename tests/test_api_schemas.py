
from uuid import uuid4

import pytest
from pydantic import ValidationError

from dbmonitor.api.schemas import TargetCreate, TargetResponse


def test_target_create_accepts_valid_postgresql_target():
    target = TargetCreate(
        name="Development Database",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="development-db",
    )

    assert target.engine == "postgresql"
    assert target.port == 5432
    assert target.enabled is True


def test_target_create_accepts_oracle_target():
    target = TargetCreate(
        name="Oracle Database",
        engine="oracle",
        host="localhost",
        port=1521,
        database_name="ORCL",
        credential_ref="oracle-dev",
    )

    assert target.engine == "oracle"


def test_target_create_rejects_unsupported_engine():
    with pytest.raises(ValidationError):
        TargetCreate(
            name="Unsupported Database",
            engine="mysql",
            host="localhost",
            port=3306,
            database_name="app_db",
            credential_ref="development-db",
        )


def test_target_create_rejects_invalid_port():
    with pytest.raises(ValidationError):
        TargetCreate(
            name="Development Database",
            engine="postgresql",
            host="localhost",
            port=70000,
            database_name="app_db",
            credential_ref="development-db",
        )


def test_target_create_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        TargetCreate(
            name="Development Database",
            engine="postgresql",
            host="localhost",
            port=5432,
            database_name="app_db",
            credential_ref="development-db",
            id=str(uuid4()),
        )


def test_target_response_does_not_expose_credential_reference():
    response = TargetResponse(
        id=uuid4(),
        name="Development Database",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        enabled=True,
    )

    assert "credential_ref" not in response.model_dump()
