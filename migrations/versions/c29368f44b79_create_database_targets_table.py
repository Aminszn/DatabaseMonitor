
"""create database targets table

Revision ID: c29368f44b79
Revises: a6980773a9c7
Create Date: 2026-10-24 20:43:02.065523
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c29368f44b79"
down_revision: Union[str, Sequence[str], None] = "a6980773a9c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the database targets table."""
    op.create_table(
        "database_targets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("engine", sa.String(length=20), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column(
            "database_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "credential_ref",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove the database targets table."""
    op.drop_table("database_targets")
