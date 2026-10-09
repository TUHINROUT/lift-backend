from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import TimestampMixin
from app.db.base import Base
from app.modules.users.models import User

class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "date",
            name="uq_attendance_user_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    punch_in_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    punch_in_latitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    punch_in_longitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    punch_out_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    punch_out_latitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    punch_out_longitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )

    working_hours: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    user = relationship(
        "User",
    )