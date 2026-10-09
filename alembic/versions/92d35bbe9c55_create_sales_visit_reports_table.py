"""create sales visit reports table

Revision ID: 92d35bbe9c55
Revises: 24664f9a4f18
Create Date: 2026-09-30 16:23:45.032624

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "92d35bbe9c55"
down_revision: Union[str, Sequence[str], None] = "24664f9a4f18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sales visit reports table."""

    op.create_table(
        "sales_visit_reports",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "report_number",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "client_name",
            sa.String(length=200),
            nullable=False,
        ),

        sa.Column(
            "contact_person",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "location",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "lift_type",
            sa.String(length=200),
            nullable=False,
        ),

        sa.Column(
            "units",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "estimated_quote",
            sa.Numeric(
                precision=14,
                scale=2,
            ),
            nullable=False,
        ),

        sa.Column(
            "visit_date",
            sa.Date(),
            nullable=False,
        ),

        sa.Column(
            "visit_time",
            sa.Time(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "NEW_LEAD",
                "NEGOTIATION",
                "FOLLOW_UP_NEEDED",
                "DEAL_CLOSED",
                name="salesvisitstatus",
            ),
            nullable=False,
        ),

        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "site_image",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        "ix_sales_visit_reports_id",
        "sales_visit_reports",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_sales_visit_reports_report_number",
        "sales_visit_reports",
        ["report_number"],
        unique=True,
    )


def downgrade() -> None:
    """Drop sales visit reports table."""

    op.drop_index(
        "ix_sales_visit_reports_report_number",
        table_name="sales_visit_reports",
    )

    op.drop_index(
        "ix_sales_visit_reports_id",
        table_name="sales_visit_reports",
    )

    op.drop_table(
        "sales_visit_reports",
    )