from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base


class Role(Base, TimestampMixin, ActiveMixin):
    """
    Role master.
    Used for authorization.
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    role_code: Mapped[str] = mapped_column(
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
        back_populates="role",
    )