from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import TimestampMixin
from app.db.base import Base


class EmployeeTracking(Base, TimestampMixin):
    __tablename__ = "employee_tracking"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    client_record_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    attendance_id: Mapped[int] = mapped_column(
        ForeignKey("attendance.id"),
        nullable=False,
        index=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    latitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
        nullable=False,
    )

    battery_percentage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    attendance = relationship(
        "Attendance",
    )

    employee = relationship(
        "User",
    )