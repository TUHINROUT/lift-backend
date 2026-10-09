from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.attendance.models import Attendance
from app.modules.tasks.models import Task
from app.modules.users.models import User
from app.modules.roles.models import Role
from datetime import date


class AttendanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_attendance_users(
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
                    Role.name.in_(
                        ["MANAGER", "EMPLOYEE", "TECHNICIAN"]
                    )
                ),
            )
            .order_by(
                User.first_name,
                User.last_name,
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )
    
    async def get_attendance_by_date(
        self,
        attendance_date: date,
    ) -> list[Attendance]:

        stmt = (
            select(Attendance)
            .options(
                selectinload(Attendance.user),
            )
            .where(
                Attendance.date == attendance_date,
            )
            .order_by(
                Attendance.user_id,
            )
        )

        result = await self.db.execute(stmt)

        return list(
            result.scalars().all()
        )
    

    async def get_by_user_and_date(
        self,
        user_id: int,
        attendance_date: date,
    ) -> Attendance | None:

        stmt = (
            select(Attendance)
            .options(
                selectinload(Attendance.user),
            )
            .where(
                Attendance.user_id == user_id,
                Attendance.date == attendance_date,
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_user(
            self,
            user_id: int,
        ) -> list[Attendance]:
    
            stmt = (
                select(Attendance)
                .options(
                    selectinload(Attendance.user),
                )
                .where(Attendance.user_id == user_id)
                .order_by(
                    Attendance.date.desc(),
                    Attendance.id.desc(),
                )
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
    
    async def get_open_attendance(
        self,
    ) -> list[Attendance]:

        stmt = (
            select(Attendance)
            .where(
                Attendance.punch_in_time.is_not(None),
                Attendance.punch_out_time.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        attendance: Attendance,
    ) -> Attendance:

        self.db.add(attendance)

        await self.db.commit()

        stmt = (
            select(Attendance)
            .options(
                selectinload(Attendance.user),
            )
            .where(Attendance.id == attendance.id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()

    async def update(
        self,
        attendance: Attendance,
    ) -> Attendance:

        await self.db.commit()

        stmt = (
            select(Attendance)
            .options(
                selectinload(Attendance.user),
            )
            .where(Attendance.id == attendance.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_by_id(
        self,
        attendance_id: int,
    ) -> Attendance | None:

        stmt = (
            select(Attendance)
            .options(
                selectinload(Attendance.user),
            )
            .where(Attendance.id == attendance_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[Attendance]:

        stmt = (
            select(Attendance)
            .options(
                selectinload(Attendance.user),
            )
            .order_by(
                Attendance.date.desc(),
                Attendance.id.desc(),
            )
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    async def get_active_tasks_by_employee(
        self,
        employee_id: int,
    ) -> list[Task]:

        stmt = (
            select(Task)
            .where(
                Task.assigned_to == employee_id,
                Task.is_active == True,
                Task.status.in_([
                "PENDING",
                "IN_PROGRESS",
            ]),
            )
            .order_by(Task.created_at.desc())
            .limit(1)

        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())


    async def has_in_progress_task(
        self, 
        employee_id: int,
    ) -> bool:

        stmt = (
            select(Task.id)
            .where(
                Task.assigned_to == employee_id,
                Task.is_active.is_(True),
                Task.status == "IN_PROGRESS",
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none() is not None