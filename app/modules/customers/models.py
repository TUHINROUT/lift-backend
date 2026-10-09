from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base


class Customer(Base, TimestampMixin, ActiveMixin):

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    customer_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    project_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    mobile: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    alternate_mobile: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    gst_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    lifts = relationship(
        "Lift",
        back_populates="customer",
    )