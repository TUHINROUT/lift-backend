from datetime import date,datetime
from sqlalchemy import Date, ForeignKey, Numeric, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.mixins import ActiveMixin, TimestampMixin
from app.db.base import Base

class Task(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    task_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    lift_id: Mapped[int] = mapped_column(
        ForeignKey("lifts.id"),
        nullable=False,
    )

    assigned_to: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    assigned_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    sub_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    ticket_id: Mapped[int | None] = mapped_column(
        ForeignKey("tickets.id"),
        nullable=True,
    )

    due_date: Mapped[date] = mapped_column(
        Date,
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
    location_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    allowed_radius: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attachment: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    lift = relationship(
        "Lift",
        back_populates="tasks",
    )

    assigned_employee = relationship(
        "User",
        foreign_keys=[assigned_to],
    )

    assigned_manager = relationship(
        "User",
        foreign_keys=[assigned_by],
    )
    @property
    def assigned_by_name(self) -> str:
        if self.assigned_manager:
            return (
                f"{self.assigned_manager.first_name} "
                f"{self.assigned_manager.last_name}"
            ).strip()

        return ""

    ticket = relationship(
        "Ticket",
        back_populates="tasks",
    )

class TaskExecution(Base, TimestampMixin):
    __tablename__ = "task_executions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    start_latitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )
    start_longitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )
    completed_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_latitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )
    completed_longitude: Mapped[float | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    client_signature: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    client_photo: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    task = relationship(
        "Task",
    )
    employee = relationship(
        "User",
    )

class TaskQuestion(Base, TimestampMixin):
    __tablename__ = "task_questions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False,
        index=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    task = relationship(
        "Task",
    )

class TaskAnswer(Base, TimestampMixin):
    __tablename__ = "task_answers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    execution_id: Mapped[int] = mapped_column(
        ForeignKey("task_executions.id"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("task_questions.id"),
        nullable=False,
        index=True,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    execution = relationship(
        "TaskExecution",
    )

    question = relationship(
        "TaskQuestion",
    )