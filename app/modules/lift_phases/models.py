from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import LiftPhase
from app.common.mixins import TimestampMixin
from app.db.base import Base


class LiftPhaseHistory(Base, TimestampMixin):
    __tablename__ = "lift_phase_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    lift_id: Mapped[int] = mapped_column(
        ForeignKey("lifts.id"),
        nullable=False,
        index=True,
    )

    phase: Mapped[LiftPhase] = mapped_column(
        Enum(LiftPhase),
        nullable=False,
    )

    completed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    lift = relationship(
        "Lift",
    )

    completed_by_user = relationship(
        "User",
    )