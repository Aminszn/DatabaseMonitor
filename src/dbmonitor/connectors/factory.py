
from psycopg.conninfo import make_conninfo

from dbmonitor.connectors.base import BaseConnector
from dbmonitor.connectors.oracle import OracleConnector
from dbmonitor.connectors.postgres import PostgresConnector
from dbmonitor.models.targets import DatabaseTarget
from dbmonitor.services.credentials import EnvironmentCredentialProvider


class ConnectorFactory:
    """Create database connectors from target configuration."""

    def __init__(
        self,
        credential_provider: EnvironmentCredentialProvider | None = None,
        connect_timeout_seconds: int = 10,
    ) -> None:
        if connect_timeout_seconds <= 0:
            raise ValueError("Connection timeout must be positive.")

        self._credential_provider = (
            credential_provider or EnvironmentCredentialProvider()
        )
        self._connect_timeout_seconds = connect_timeout_seconds

    def create(self, target: DatabaseTarget) -> BaseConnector:
        """Resolve credentials and create the appropriate connector."""
        credentials = self._credential_provider.resolve(
            target.credential_ref
        )

        if target.engine == "postgresql":
            connection_string = make_conninfo(
                host=target.host,
                port=target.port,
                dbname=target.database_name,
                user=credentials.username,
                password=credentials.password,
                connect_timeout=self._connect_timeout_seconds,
            )

            return PostgresConnector(
                connection_string=connection_string,
                connect_timeout_seconds=self._connect_timeout_seconds,
            )

        if target.engine == "oracle":
            dsn = f"{target.host}:{target.port}/{target.database_name}"

            return OracleConnector(
                username=credentials.username,
                password=credentials.password,
                dsn=dsn,
            )

        raise ValueError(f"Unsupported database engine: {target.engine}")
