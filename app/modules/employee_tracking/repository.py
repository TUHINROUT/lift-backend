from datetime import date, datetime, time

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.employee_tracking.models import EmployeeTracking


class EmployeeTrackingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tracking: EmployeeTracking,
    ) -> EmployeeTracking:

        self.db.add(tracking)

        await self.db.commit()

        await self.db.refresh(tracking)

        return tracking

    async def create_many(
        self,
        tracking_records: list[EmployeeTracking],
    ) -> None:

        if not tracking_records:
            return

        values = [
            {
                "client_record_id": tracking.client_record_id,
                "employee_id": tracking.employee_id,
                "attendance_id": tracking.attendance_id,
                "recorded_at": tracking.recorded_at,
                "latitude": tracking.latitude,
                "longitude": tracking.longitude,
                "battery_percentage": tracking.battery_percentage,
            }
            for tracking in tracking_records
        ]

        stmt = (
            insert(EmployeeTracking)
            .values(values)
            .on_conflict_do_nothing(
                index_elements=[
                    EmployeeTracking.client_record_id
                ]
            )
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def get_by_employee(
        self,
        employee_id: int,
    ) -> list[EmployeeTracking]:

        stmt = (
            select(EmployeeTracking)
            .options(
                selectinload(EmployeeTracking.employee),
            )
            .where(
                EmployeeTracking.employee_id == employee_id,
            )
            .order_by(
                EmployeeTracking.recorded_at.asc(),
            )
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_employee(
        self,
        employee_id: int,
    ) -> EmployeeTracking | None:

        stmt = (
            select(EmployeeTracking)
            .options(
                selectinload(EmployeeTracking.employee),
            )
            .where(
                EmployeeTracking.employee_id == employee_id,
            )
            .order_by(
                EmployeeTracking.recorded_at.desc(),
            )
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_attendance(
        self,
        attendance_id: int,
    ) -> list[EmployeeTracking]:

        stmt = (
            select(EmployeeTracking)
            .where(
                EmployeeTracking.attendance_id == attendance_id,
            )
            .order_by(
                EmployeeTracking.recorded_at.asc(),
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_older_than(
        self,
        cutoff: datetime,
    ) -> int:

        stmt = delete(EmployeeTracking).where(
            EmployeeTracking.recorded_at < cutoff,
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount or 0

    async def get_existing_client_record_ids(
        self,
        client_record_ids: list[str],
    ) -> set[str]:

        if not client_record_ids:
            return set()

        stmt = (
            select(EmployeeTracking.client_record_id)
            .where(
                EmployeeTracking.client_record_id.in_(
                    client_record_ids
                )
            )
        )

        result = await self.db.execute(stmt)

        return set(result.scalars().all())

    async def get_by_employee_and_date(
        self,
        employee_id: int,
        tracking_date: date,
    ) -> list[EmployeeTracking]:

        start_datetime = datetime.combine(
            tracking_date,
            time.min,
        )

        end_datetime = datetime.combine(
            tracking_date,
            time.max,
        )

        stmt = (
            select(EmployeeTracking)
            .options(
                selectinload(EmployeeTracking.employee),
            )
            .where(
                EmployeeTracking.employee_id == employee_id,
                EmployeeTracking.recorded_at >= start_datetime,
                EmployeeTracking.recorded_at <= end_datetime,
            )
            .order_by(
                EmployeeTracking.recorded_at.asc(),
            )
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())