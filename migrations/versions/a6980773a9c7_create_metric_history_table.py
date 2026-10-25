
"""create metric history table

Revision ID: a6980773a9c7
Revises:
Create Date: 2026-10-24 20:31:24.481580
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6980773a9c7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the metric history table."""
    op.create_table(
        "metric_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("engine", sa.String(length=20), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Numeric(), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_metric_history_target_id",
        "metric_history",
        ["target_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the metric history table."""
    op.drop_index(
        "ix_metric_history_target_id",
        table_name="metric_history",
    )
    op.drop_table("metric_history")
