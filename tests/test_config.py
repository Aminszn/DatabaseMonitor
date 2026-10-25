
from dbmonitor.config import Settings, get_settings


def test_default_settings():
    settings = Settings(_env_file=None)

    assert settings.app_name == "Database Health Monitor"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8000
    assert settings.monitoring_interval_seconds == 60
    assert settings.log_level == "INFO"


def test_monitoring_database_url_is_optional():
    settings = Settings(_env_file=None)

    assert settings.monitoring_database_url is None


def test_get_settings_returns_cached_instance():
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
