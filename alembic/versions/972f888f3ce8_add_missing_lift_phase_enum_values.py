"""add missing lift phase enum values

Revision ID: 972f888f3ce8
Revises: c922177cab68
Create Date: 2026-08-24 13:06:14.827604

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "972f888f3ce8"
down_revision: Union[str, Sequence[str], None] = "c922177cab68"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE liftphase ADD VALUE IF NOT EXISTS 'MANUFACTURING'"
    )
    op.execute(
        "ALTER TYPE liftphase ADD VALUE IF NOT EXISTS 'INSTALLATION'"
    )
    op.execute(
        "ALTER TYPE liftphase ADD VALUE IF NOT EXISTS 'TESTING'"
    )


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly.
    pass
