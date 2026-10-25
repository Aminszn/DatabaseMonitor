
import pytest

from dbmonitor.services.credentials import (
    DatabaseCredentials,
    EnvironmentCredentialProvider,
)


@pytest.fixture
def provider():
    return EnvironmentCredentialProvider()


def test_resolve_returns_credentials(provider, monkeypatch):
    monkeypatch.setenv(
        "DBMONITOR_CREDENTIAL_DEVELOPMENT_DB_USERNAME",
        "monitor_user",
    )
    monkeypatch.setenv(
        "DBMONITOR_CREDENTIAL_DEVELOPMENT_DB_PASSWORD",
        "test-secret",
    )

    credentials = provider.resolve("development-db")

    assert isinstance(credentials, DatabaseCredentials)
    assert credentials.username == "monitor_user"
    assert credentials.password == "test-secret"


def test_resolve_raises_when_credentials_are_missing(
    provider,
    monkeypatch,
):
    monkeypatch.delenv(
        "DBMONITOR_CREDENTIAL_MISSING_DB_USERNAME",
        raising=False,
    )
    monkeypatch.delenv(
        "DBMONITOR_CREDENTIAL_MISSING_DB_PASSWORD",
        raising=False,
    )

    with pytest.raises(RuntimeError, match="Credentials are missing"):
        provider.resolve("missing-db")


def test_resolve_rejects_invalid_reference(provider):
    with pytest.raises(ValueError, match="Invalid credential reference"):
        provider.resolve("development db")


def test_password_is_not_shown_in_credentials_repr():
    credentials = DatabaseCredentials(
        username="monitor_user",
        password="test-secret",
    )

    assert "test-secret" not in repr(credentials)
