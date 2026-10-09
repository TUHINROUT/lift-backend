from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base


class Department(Base, TimestampMixin, ActiveMixin):
    """
    Department master.
    """

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    department_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    users = relationship(
        "User",
        back_populates="department",
    )