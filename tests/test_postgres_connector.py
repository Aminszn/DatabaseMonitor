
from decimal import Decimal
from unittest.mock import MagicMock, patch

import psycopg
import pytest

from dbmonitor.connectors.postgres import PostgresConnector


@pytest.fixture
def connector():
    return PostgresConnector(
        connection_string="postgresql://monitor:secret@localhost/testdb",
        connect_timeout_seconds=5,
    )


def test_connector_rejects_empty_connection_string():
    with pytest.raises(ValueError):
        PostgresConnector("")


def test_connector_rejects_invalid_timeout():
    with pytest.raises(ValueError):
        PostgresConnector("postgresql://localhost/testdb", 0)


@patch("dbmonitor.connectors.postgres.psycopg.connect")
def test_connect_establishes_connection(mock_connect, connector):
    mock_connect.return_value = MagicMock(closed=False)

    connector.connect()

    mock_connect.assert_called_once_with(
        "postgresql://monitor:secret@localhost/testdb",
        connect_timeout=5,
    )


@patch("dbmonitor.connectors.postgres.psycopg.connect")
def test_connect_reuses_open_connection(mock_connect, connector):
    mock_connection = MagicMock(closed=False)
    connector._connection = mock_connection

    connector.connect()

    mock_connect.assert_not_called()


def test_close_releases_connection(connector):
    mock_connection = MagicMock(closed=False)
    connector._connection = mock_connection

    connector.close()

    mock_connection.close.assert_called_once()
    assert connector._connection is None


@patch.object(PostgresConnector, "execute_query")
def test_health_check_returns_true(mock_execute, connector):
    mock_execute.return_value = [{"health_check": 1}]

    assert connector.check_health() is True


@patch.object(PostgresConnector, "execute_query")
def test_health_check_returns_false_on_database_error(
    mock_execute,
    connector,
):
    mock_execute.side_effect = psycopg.OperationalError("Connection lost")

    assert connector.check_health() is False


@patch.object(PostgresConnector, "execute_query")
def test_get_sessions_returns_counts(mock_execute, connector):
    mock_execute.return_value = [{"active": 3, "idle": 7}]

    assert connector.get_sessions() == {"active": 3, "idle": 7}


@patch.object(PostgresConnector, "execute_query")
def test_get_database_size_returns_decimal(mock_execute, connector):
    mock_execute.return_value = [{"size_bytes": 4096}]

    assert connector.get_database_size() == Decimal("4096")


@patch("dbmonitor.connectors.postgres.psycopg.connect")
def test_execute_query_returns_dictionary_rows(mock_connect, connector):
    mock_connection = MagicMock(closed=False)
    mock_cursor = MagicMock()

    mock_cursor.description = [("health_check",)]
    mock_cursor.fetchall.return_value = [{"health_check": 1}]
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    rows = connector.execute_query("SELECT 1 AS health_check")

    assert rows == [{"health_check": 1}]
    mock_cursor.execute.assert_called_once_with(
        "SELECT 1 AS health_check",
        None,
    )
