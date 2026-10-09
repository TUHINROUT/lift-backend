from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import (
    TicketPriority,
    TicketStatus,
    TicketType,
)
from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base


class Ticket(Base, TimestampMixin, ActiveMixin):
    """
    Customer complaint / service ticket.

    A Ticket represents a customer issue.
    One Ticket can generate one or many Tasks.
    """

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    ticket_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )

    contact_person: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    contact_number: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    lift_id: Mapped[int] = mapped_column(
        ForeignKey("lifts.id"),
        nullable=False,
    )

    ticket_type: Mapped[TicketType] = mapped_column(
        Enum(TicketType),
        nullable=False,
    )

    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority),
        nullable=False,
    )

    complaint_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        nullable=False,
        default=TicketStatus.OPEN,
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    closed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closing_remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -----------------------------
    # Relationships
    # -----------------------------

    customer = relationship(
        "Customer",
    )

    lift = relationship(
        "Lift",
    )

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
    )

    closed_by_user = relationship(
        "User",
        foreign_keys=[closed_by],
    )

    tasks = relationship(
        "Task",
        back_populates="ticket",
    )