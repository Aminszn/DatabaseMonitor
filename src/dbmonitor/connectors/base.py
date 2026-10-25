
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Mapping


class BaseConnector(ABC):
    """Common interface for supported database connectors."""

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the target database."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        raise NotImplementedError

    @abstractmethod
    def check_health(self) -> bool:
        """Return whether the target database responds to a health check."""
        raise NotImplementedError

    @abstractmethod
    def get_sessions(self) -> Mapping[str, int]:
        """Return normalized session counts."""
        raise NotImplementedError

    @abstractmethod
    def get_database_size(self) -> Decimal:
        """Return the database size in bytes."""
        raise NotImplementedError

    @abstractmethod
    def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a query and return rows as dictionaries."""
        raise NotImplementedError
