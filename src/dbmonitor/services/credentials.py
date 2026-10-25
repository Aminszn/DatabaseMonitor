
import os
import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatabaseCredentials:
    """Credentials used to authenticate to a database."""

    username: str
    password: str = field(repr=False)


class EnvironmentCredentialProvider:
    """Resolve database credentials from environment variables."""

    _REFERENCE_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

    def resolve(self, credential_ref: str) -> DatabaseCredentials:
        """Resolve a credential reference into username and password."""
        if not self._REFERENCE_PATTERN.fullmatch(credential_ref):
            raise ValueError("Invalid credential reference format.")

        normalized_ref = credential_ref.upper().replace("-", "_")
        prefix = f"DBMONITOR_CREDENTIAL_{normalized_ref}"

        username = os.environ.get(f"{prefix}_USERNAME")
        password = os.environ.get(f"{prefix}_PASSWORD")

        if not username or not password:
            raise RuntimeError(
                f"Credentials are missing for reference "
                f"'{credential_ref}'."
            )

        return DatabaseCredentials(
            username=username,
            password=password,
        )
