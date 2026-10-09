from datetime import date, time
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base


class SalesVisitStatus(str, PyEnum):
    NEW_LEAD = "New Lead"
    NEGOTIATION = "Negotiation"
    FOLLOW_UP_NEEDED = "Follow-up Needed"
    DEAL_CLOSED = "Deal Closed"


class SalesVisit(Base, TimestampMixin, ActiveMixin):
    """
    Field sales / client visit report.

    A SalesVisit represents a field visit submitted by a sales employee.
    The logged-in user is stored as the creator of the report.
    """

    __tablename__ = "sales_visit_reports"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    report_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    client_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    contact_person: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    lift_type: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    units: Mapped[int] = mapped_column(
        nullable=False,
    )

    estimated_quote: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    visit_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    visit_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[SalesVisitStatus] = mapped_column(
        Enum(
            SalesVisitStatus,
            name="salesvisitstatus",
        ),
        nullable=False,
        default=SalesVisitStatus.NEW_LEAD,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    site_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
    )