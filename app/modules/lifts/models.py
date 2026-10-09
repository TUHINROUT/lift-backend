from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base


class Lift(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "lifts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    lift_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
    )

    building_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Numeric(10, 7),
        nullable=False,
    )

    installation_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    warranty: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    amc: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    capacity: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    lift_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    machine_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    controller_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    door_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    stops: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    floors: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    serial_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    drawing: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    customer = relationship(
        "Customer",
        back_populates="lifts",
    )
    
    tasks = relationship(
        "Task",
        back_populates="lift",
    )

    @property
    def project_name(self) -> str:
        return self.customer.project_name


    @property
    def customer_code(self) -> str:
        return self.customer.customer_code