
from uuid import uuid4

import pytest
from pydantic import ValidationError

from dbmonitor.models.targets import DatabaseTarget


@pytest.fixture
def target_data():
    return {
        "id": uuid4(),
        "name": "Development Database",
        "engine": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database_name": "app_db",
        "credential_ref": "development-db",
    }


def test_create_database_target(target_data):
    target = DatabaseTarget(**target_data)

    assert target.id == target_data["id"]
    assert target.name == "Development Database"
    assert target.engine == "postgresql"
    assert target.host == "localhost"
    assert target.port == 5432
    assert target.database_name == "app_db"
    assert target.credential_ref == "development-db"
    assert target.enabled is True


def test_create_oracle_target(target_data):
    target_data.update(
        engine="oracle",
        port=1521,
        database_name="FREEPDB1",
    )

    target = DatabaseTarget(**target_data)

    assert target.engine == "oracle"
    assert target.port == 1521
    assert target.database_name == "FREEPDB1"


def test_reject_unsupported_engine(target_data):
    target_data["engine"] = "mysql"

    with pytest.raises(ValidationError):
        DatabaseTarget(**target_data)


@pytest.mark.parametrize("port", [0, 65536])
def test_reject_invalid_port(target_data, port):
    target_data["port"] = port

    with pytest.raises(ValidationError):
        DatabaseTarget(**target_data)


def test_target_is_immutable(target_data):
    target = DatabaseTarget(**target_data)

    with pytest.raises(ValidationError):
        target.enabled = False


def test_reject_empty_credential_reference(target_data):
    target_data["credential_ref"] = ""

    with pytest.raises(ValidationError):
        DatabaseTarget(**target_data)
