from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.lifts.models import Lift
from app.modules.tasks.models import (
    Task,
    TaskExecution,
    TaskQuestion,
    TaskAnswer,
)
from app.modules.tickets.models import Ticket
from app.modules.lift_phases.models import LiftPhaseHistory
from app.modules.attendance.models import Attendance
from app.modules.users.models import User
from app.modules.roles.models import Role


class ReportRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def get_active_users_for_attendance_report(
        self,
    ) -> list[User]:
        stmt = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.department),
                selectinload(User.designation),
            )
            .where(
                User.is_active.is_(True),
                User.role.has(
                    Role.name.in_(["MANAGER", "EMPLOYEE"])
                ),
            )
            .order_by(
                User.first_name,
                User.last_name,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


    async def get_attendance_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[Attendance]:

        stmt = (
            select(Attendance)
            .where(
                Attendance.date >= start_date,
                Attendance.date <= end_date,
            )
            .order_by(
                Attendance.date,
                Attendance.user_id,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    

    async def get_lift_by_code(
        self,
        lift_code: str,
    ) -> Lift | None:

        stmt = (
            select(Lift)
            .options(
                selectinload(
                    Lift.customer
                )
            )
            .where(
                Lift.lift_code == lift_code
            )
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_tasks_by_lift(
        self,
        lift_id: int,
    ) -> list[Task]:

        stmt = (
            select(Task)
            .options(
                selectinload(
                    Task.assigned_employee
                ),
                selectinload(
                    Task.assigned_manager
                ),
                selectinload(
                    Task.ticket
                ),
            )
            .where(
                Task.lift_id == lift_id
            )
            .order_by(
                Task.id
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )

    async def get_phase_history_by_lift(
        self,
        lift_id: int,
    ) -> list[LiftPhaseHistory]:

        stmt = (
            select(LiftPhaseHistory)
            .options(
                selectinload(
                    LiftPhaseHistory.completed_by_user
                )
            )
            .where(
                LiftPhaseHistory.lift_id == lift_id
            )
            .order_by(
                LiftPhaseHistory.completed_at
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )

    async def get_execution_by_task(
        self,
        task_id: int,
    ) -> TaskExecution | None:

        stmt = (
            select(TaskExecution)
            .where(
                TaskExecution.task_id == task_id
            )
            .order_by(
                TaskExecution.id.desc()
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_questions_by_task(
        self,
        task_id: int,
    ) -> list[TaskQuestion]:

        stmt = (
            select(TaskQuestion)
            .where(
                TaskQuestion.task_id == task_id
            )
            .order_by(
                TaskQuestion.id
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )

    async def get_answers_by_execution(
        self,
        execution_id: int,
    ) -> list[TaskAnswer]:

        stmt = (
            select(TaskAnswer)
            .where(
                TaskAnswer.execution_id == execution_id
            )
            .order_by(
                TaskAnswer.id
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )

    async def get_tickets_by_lift(
        self,
        lift_id: int,
    ) -> list[Ticket]:

        stmt = (
            select(Ticket)
            .where(
                Ticket.lift_id == lift_id
            )
            .order_by(
                Ticket.id
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )