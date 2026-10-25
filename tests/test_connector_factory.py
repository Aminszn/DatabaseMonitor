
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from dbmonitor.connectors.factory import ConnectorFactory
from dbmonitor.connectors.oracle import OracleConnector
from dbmonitor.connectors.postgres import PostgresConnector
from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.services.credentials import DatabaseCredentials


@pytest.fixture
def credential_provider():
    provider = MagicMock()
    provider.resolve.return_value = DatabaseCredentials(
        username="monitor_user",
        password="test-secret",
    )
    return provider


@pytest.fixture
def factory(credential_provider):
    return ConnectorFactory(
        credential_provider=credential_provider,
        connect_timeout_seconds=5,
    )


@pytest.fixture
def postgres_target():
    return DatabaseTarget(
        id=uuid4(),
        name="Development PostgreSQL",
        engine="postgresql",
        host="localhost",
        port=5432,
        database_name="app_db",
        credential_ref="development-db",
    )


@pytest.fixture
def oracle_target():
    return DatabaseTarget(
        id=uuid4(),
        name="Development Oracle",
        engine="oracle",
        host="localhost",
        port=1521,
        database_name="FREEPDB1",
        credential_ref="development-db",
    )


def test_create_postgres_connector(
    factory,
    credential_provider,
    postgres_target,
):
    connector = factory.create(postgres_target)

    assert isinstance(connector, PostgresConnector)
    assert "host=localhost" in connector._connection_string
    assert "port=5432" in connector._connection_string
    assert "dbname=app_db" in connector._connection_string
    assert "user=monitor_user" in connector._connection_string
    assert "password=test-secret" in connector._connection_string
    assert connector._connect_timeout_seconds == 5

    credential_provider.resolve.assert_called_once_with(
        "development-db"
    )


def test_create_oracle_connector(
    factory,
    credential_provider,
    oracle_target,
):
    connector = factory.create(oracle_target)

    assert isinstance(connector, OracleConnector)
    assert connector._username == "monitor_user"
    assert connector._password == "test-secret"
    assert connector._dsn == "localhost:1521/FREEPDB1"

    credential_provider.resolve.assert_called_once_with(
        "development-db"
    )


def test_factory_rejects_nonpositive_timeout():
    with pytest.raises(ValueError, match="Connection timeout"):
        ConnectorFactory(connect_timeout_seconds=0)
