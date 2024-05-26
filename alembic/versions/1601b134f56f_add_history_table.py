"""Add History Table

Revision ID: 1601b134f56f
Revises: ba1a57082a3b
Create Date: 2024-05-26 12:17:22.350501

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1601b134f56f"
down_revision: Union[str, None] = "ba1a57082a3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column(
            "type", sa.Enum("TASK_DELETED", name="historyentrytype"), nullable=False
        ),
        sa.Column(
            "version", sa.Enum("TASK", name="historyentryversion"), nullable=False
        ),
        sa.Column("event", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("history")
    # ### end Alembic commands ###