from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.mixins import TimestampMixin, ActiveMixin
from app.db.base import Base


class User(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    employee_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    profile_photo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    company_id: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    designation_id: Mapped[int | None] = mapped_column(
            ForeignKey("designations.id"),
            nullable=True,
        )

    department_id: Mapped[int | None] = mapped_column(
            ForeignKey("departments.id"),
            nullable=True,
        )
    
    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("roles.id"),
        nullable=True,
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    designation = relationship(
        "Designation",
        back_populates="users",
    )

    department = relationship(
        "Department",
        back_populates="users",
    )
    role = relationship(
        "Role",
        back_populates="users",
    )

    @property
    def designation_name(self) -> str | None:
        if self.designation:
            return self.designation.name
        return None


    @property
    def department_name(self) -> str | None:
        if self.department:
            return self.department.name
        return None

    @property
    def role_name(self) -> str | None:
        if self.role:
            return self.role.name
        return None