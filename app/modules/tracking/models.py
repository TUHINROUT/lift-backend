from datetime import datetime
from sqlalchemy import Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.mixins import TimestampMixin
from app.db.base import Base


class EmployeeLocation(Base, TimestampMixin):
    __tablename__ = "employee_locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    speed: Mapped[float] = mapped_column(Float, default=0.0)
    heading: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="On Route")
    current_destination: Mapped[str | None] = mapped_column(String(255), nullable=True)
    battery_level: Mapped[int] = mapped_column(Integer, default=100)

    user = relationship("User", backref="latest_location")