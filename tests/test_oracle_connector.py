
from decimal import Decimal
from unittest.mock import MagicMock, patch

import oracledb
import pytest

from dbmonitor.connectors.oracle import OracleConnector


@pytest.fixture
def connector():
    return OracleConnector(
        username="monitor",
        password="test-secret",
        dsn="localhost:1521/FREEPDB1",
    )


def test_connector_rejects_empty_username():
    with pytest.raises(ValueError):
        OracleConnector("", "password", "localhost:1521/FREEPDB1")


def test_connector_rejects_empty_password():
    with pytest.raises(ValueError):
        OracleConnector("monitor", "", "localhost:1521/FREEPDB1")


def test_connector_rejects_empty_dsn():
    with pytest.raises(ValueError):
        OracleConnector("monitor", "password", "")


@patch("dbmonitor.connectors.oracle.oracledb.connect")
def test_connect_establishes_connection(mock_connect, connector):
    mock_connect.return_value = MagicMock()

    connector.connect()

    mock_connect.assert_called_once_with(
        user="monitor",
        password="test-secret",
        dsn="localhost:1521/FREEPDB1",
    )


@patch("dbmonitor.connectors.oracle.oracledb.connect")
def test_connect_reuses_existing_connection(mock_connect, connector):
    mock_connection = MagicMock()
    connector._connection = mock_connection

    connector.connect()

    mock_connect.assert_not_called()


def test_close_releases_connection(connector):
    mock_connection = MagicMock()
    connector._connection = mock_connection

    connector.close()

    mock_connection.close.assert_called_once()
    assert connector._connection is None


@patch.object(OracleConnector, "execute_query")
def test_health_check_returns_true(mock_execute, connector):
    mock_execute.return_value = [{"health_check": 1}]

    assert connector.check_health() is True


@patch.object(OracleConnector, "execute_query")
def test_health_check_returns_false_on_database_error(
    mock_execute,
    connector,
):
    mock_execute.side_effect = oracledb.DatabaseError("Connection lost")

    assert connector.check_health() is False


@patch.object(OracleConnector, "execute_query")
def test_get_sessions_returns_counts(mock_execute, connector):
    mock_execute.return_value = [{"active": 4, "idle": 9}]

    assert connector.get_sessions() == {"active": 4, "idle": 9}


@patch.object(OracleConnector, "execute_query")
def test_get_database_size_returns_decimal(mock_execute, connector):
    mock_execute.return_value = [{"size_bytes": 8192}]

    assert connector.get_database_size() == Decimal("8192")


@patch("dbmonitor.connectors.oracle.oracledb.connect")
def test_execute_query_returns_normalized_dictionary_rows(
    mock_connect,
    connector,
):
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.description = [
        ("HEALTH_CHECK",),
    ]
    mock_cursor.fetchall.return_value = [(1,)]
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    rows = connector.execute_query(
        "SELECT 1 AS health_check FROM dual"
    )

    assert rows == [{"health_check": 1}]
    mock_cursor.execute.assert_called_once_with(
        "SELECT 1 AS health_check FROM dual",
        None,
    )
