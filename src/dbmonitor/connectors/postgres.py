
from decimal import Decimal
from typing import Any, Mapping

import psycopg
from psycopg.rows import dict_row

from dbmonitor.connectors.base import BaseConnector


class PostgresConnector(BaseConnector):
    """Connector for monitoring a PostgreSQL database."""

    def __init__(
        self,
        connection_string: str,
        connect_timeout_seconds: int = 10,
    ) -> None:
        if not connection_string:
            raise ValueError("Connection string must not be empty.")

        if connect_timeout_seconds <= 0:
            raise ValueError("Connection timeout must be positive.")

        self._connection_string = connection_string
        self._connect_timeout_seconds = connect_timeout_seconds
        self._connection: psycopg.Connection | None = None

    def connect(self) -> None:
        """Establish a connection if one is not already open."""
        if self._connection is not None and not self._connection.closed:
            return

        self._connection = psycopg.connect(
            self._connection_string,
            connect_timeout=self._connect_timeout_seconds,
        )

    def close(self) -> None:
        """Close the connection and release its resources."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _ensure_connected(self) -> psycopg.Connection:
        """Return an open connection, establishing one if necessary."""
        self.connect()

        if self._connection is None:
            raise RuntimeError("PostgreSQL connection was not established.")

        return self._connection

    def check_health(self) -> bool:
        """Return whether a simple query succeeds."""
        try:
            rows = self.execute_query("SELECT 1 AS health_check")
            return rows == [{"health_check": 1}]
        except psycopg.Error:
            return False

    def get_sessions(self) -> Mapping[str, int]:
        """Return active and idle session counts for the current database."""
        query = """
            SELECT
                COUNT(*) FILTER (WHERE state = 'active') AS active,
                COUNT(*) FILTER (WHERE state = 'idle') AS idle
            FROM pg_stat_activity
            WHERE datname = current_database()
        """

        rows = self.execute_query(query)

        if not rows:
            raise RuntimeError("PostgreSQL returned no session statistics.")

        return {
            "active": int(rows[0]["active"]),
            "idle": int(rows[0]["idle"]),
        }

    def get_database_size(self) -> Decimal:
        """Return the current database's allocated size in bytes."""
        query = """
            SELECT pg_database_size(current_database()) AS size_bytes
        """

        rows = self.execute_query(query)

        if not rows:
            raise RuntimeError("PostgreSQL returned no database size.")

        return Decimal(rows[0]["size_bytes"])

    def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a query and return its rows as dictionaries."""
        connection = self._ensure_connected()

        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, parameters)

            if cursor.description is None:
                return []

            return [dict(row) for row in cursor.fetchall()]
