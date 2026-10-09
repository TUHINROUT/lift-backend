"""update customer_name to project_name

Revision ID: ae1ed6cb953d
Revises: cd54410b872e
Create Date: 2026-08-10 15:42:27.062106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae1ed6cb953d'
down_revision: Union[str, Sequence[str], None] = 'cd54410b872e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_index(
        op.f("ix_customers_customer_name"),
        table_name="customers",
    )

    op.alter_column(
        "customers",
        "customer_name",
        new_column_name="project_name",
    )

    op.create_index(
        op.f("ix_customers_project_name"),
        "customers",
        ["project_name"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_customers_project_name"),
        table_name="customers",
    )

    op.alter_column(
        "customers",
        "project_name",
        new_column_name="customer_name",
    )

    op.create_index(
        op.f("ix_customers_customer_name"),
        "customers",
        ["customer_name"],
        unique=False,
    )
