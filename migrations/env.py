
from logging.config import fileConfig

from alembic import context

from dbmonitor.config import get_settings
from dbmonitor.database import create_monitoring_engine
from dbmonitor.repositories.metrics_repository import metadata


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def get_database_url() -> str:
    """Get the monitoring database URL from application settings."""
    database_url = get_settings().monitoring_database_url

    if database_url is None:
        raise RuntimeError(
            "MONITORING_DATABASE_URL must be configured "
            "before running database migrations."
        )

    return database_url.get_secret_value()


def run_migrations_offline() -> None:
    """Generate migration SQL without creating a database connection."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using the monitoring database connection."""
    connectable = create_monitoring_engine()

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
