
from decimal import Decimal
from typing import Any, Mapping

import oracledb

from dbmonitor.connectors.base import BaseConnector


class OracleConnector(BaseConnector):
    """Connector for monitoring an Oracle database."""

    def __init__(
        self,
        username: str,
        password: str,
        dsn: str,
    ) -> None:
        if not username:
            raise ValueError("Oracle username must not be empty.")

        if not password:
            raise ValueError("Oracle password must not be empty.")

        if not dsn:
            raise ValueError("Oracle DSN must not be empty.")

        self._username = username
        self._password = password
        self._dsn = dsn
        self._connection: oracledb.Connection | None = None

    def connect(self) -> None:
        """Establish a connection if one is not already open."""
        if self._connection is not None:
            return

        self._connection = oracledb.connect(
            user=self._username,
            password=self._password,
            dsn=self._dsn,
        )

    def close(self) -> None:
        """Close the connection and release its resources."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _ensure_connected(self) -> oracledb.Connection:
        """Return a connection, establishing one if necessary."""
        self.connect()

        if self._connection is None:
            raise RuntimeError("Oracle connection was not established.")

        return self._connection

    def check_health(self) -> bool:
        """Return whether a simple query succeeds."""
        try:
            rows = self.execute_query("SELECT 1 AS health_check FROM dual")
            return rows == [{"health_check": 1}]
        except oracledb.Error:
            return False

    def get_sessions(self) -> Mapping[str, int]:
        """Return active and idle user session counts."""
        query = """
            SELECT
                COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) AS active,
                COUNT(CASE WHEN status = 'INACTIVE' THEN 1 END) AS idle
            FROM v$session
            WHERE type = 'USER'
        """

        rows = self.execute_query(query)

        if not rows:
            raise RuntimeError("Oracle returned no session statistics.")

        return {
            "active": int(rows[0]["active"]),
            "idle": int(rows[0]["idle"]),
        }

    def get_database_size(self) -> Decimal:
        """Return allocated datafile space in bytes."""
        query = """
            SELECT NVL(SUM(bytes), 0) AS size_bytes
            FROM dba_data_files
        """

        rows = self.execute_query(query)

        if not rows:
            raise RuntimeError("Oracle returned no database size.")

        return Decimal(rows[0]["size_bytes"])

    def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a query and return rows as lowercase-key dictionaries."""
        connection = self._ensure_connected()

        with connection.cursor() as cursor:
            cursor.execute(query, parameters)

            if cursor.description is None:
                return []

            columns = [
                description[0].lower()
                for description in cursor.description
            ]

            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
