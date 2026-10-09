from datetime import date, datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.repository import AttendanceRepository
from app.modules.employee_tracking.models import EmployeeTracking
from app.modules.employee_tracking.repository import EmployeeTrackingRepository
from app.modules.employee_tracking.schemas import (
    EmployeeTrackingBatchCreate,
    EmployeeTrackingCreate,
    EmployeeTrackingResponse,
)


class EmployeeTrackingService:

    @staticmethod
    def _to_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    
    def __init__(self, db: AsyncSession):
        self.tracking_repository = EmployeeTrackingRepository(db)
        self.attendance_repository = AttendanceRepository(db)

    async def create(
        self,
        employee_id: int,
        data: EmployeeTrackingCreate,
    ) -> EmployeeTracking:

        attendance = await self.attendance_repository.get_by_user_and_date(
            user_id=employee_id,
            attendance_date=date.today(),
        )

        if attendance is None:
            raise ValueError(
                "Punch In is required before sending tracking data."
            )

        if attendance.punch_in_time is None:
            raise ValueError(
                "Punch In is required before sending tracking data."
            )

        if data.recorded_at < attendance.punch_in_time:
            raise ValueError(
                "Tracking time cannot be before Punch In."
            )

        if (
            attendance.punch_out_time is not None
            and data.recorded_at > attendance.punch_out_time
        ):
            raise ValueError(
                "Tracking time cannot be after Punch Out."
            )
        tracking = EmployeeTracking(
            client_record_id=data.client_record_id,
            employee_id=employee_id,
            attendance_id=attendance.id,
            recorded_at=data.recorded_at,
            latitude=data.latitude,
            longitude=data.longitude,
            battery_percentage=data.battery_percentage,
        )

        return await self.tracking_repository.create(tracking)

    async def create_batch(
        self,
        employee_id: int,
        data: EmployeeTrackingBatchCreate,
    ) -> None:

        attendance = await self.attendance_repository.get_by_user_and_date(
            user_id=employee_id,
            attendance_date=date.today(),
        )

        if attendance is None:
            raise ValueError(
                "Punch In is required before sending tracking data."
            )

        if attendance.punch_in_time is None:
            raise ValueError(
                "Punch In is required before sending tracking data."
            )

        tracking_records = []

        punch_in_time = self._to_utc(
            attendance.punch_in_time
        )

        punch_out_time = (
            self._to_utc(attendance.punch_out_time)
            if attendance.punch_out_time is not None
            else None
        )

        for record in data.records:

            recorded_at = self._to_utc(
                record.recorded_at
            )

            if recorded_at < punch_in_time:
                continue

            if (
                punch_out_time is not None
                and recorded_at > punch_out_time
            ):
                continue

            tracking_records.append(
                EmployeeTracking(
                    client_record_id=record.client_record_id,
                    employee_id=employee_id,
                    attendance_id=attendance.id,
                    recorded_at=recorded_at,
                    latitude=record.latitude,
                    longitude=record.longitude,
                    battery_percentage=record.battery_percentage,
                )
            )

        if not tracking_records:
            return
        await self.tracking_repository.create_many(
            tracking_records
        )

    async def get_by_employee(
        self,
        employee_id: int,
    ) -> list[EmployeeTrackingResponse]:

        tracking_list = await self.tracking_repository.get_by_employee(
            employee_id=employee_id,
        )

        return [
            EmployeeTrackingResponse(
                id=tracking.id,
                client_record_id=tracking.client_record_id,
                employee_id=tracking.employee_id,
                employee_name=(
                    f"{tracking.employee.first_name} "
                    f"{tracking.employee.last_name}"
                ),
                attendance_id=tracking.attendance_id,
                recorded_at=tracking.recorded_at,
                latitude=float(tracking.latitude),
                longitude=float(tracking.longitude),
                battery_percentage=tracking.battery_percentage,
            )
            for tracking in tracking_list
        ]

    async def get_latest_by_employee(
        self,
        employee_id: int,
    ) -> EmployeeTrackingResponse | None:

        tracking = await self.tracking_repository.get_latest_by_employee(
            employee_id=employee_id,
        )
        if tracking is None:
            return None
        return EmployeeTrackingResponse(
            id=tracking.id,
            client_record_id=tracking.client_record_id,
            employee_id=tracking.employee_id,
            employee_name=(
                f"{tracking.employee.first_name} "
                f"{tracking.employee.last_name}"
            ),
            attendance_id=tracking.attendance_id,
            recorded_at=tracking.recorded_at,
            latitude=float(tracking.latitude),
            longitude=float(tracking.longitude),
            battery_percentage=tracking.battery_percentage,
        )

    async def get_by_attendance(
        self,
        attendance_id: int,
    ) -> list[EmployeeTracking]:

        return await self.tracking_repository.get_by_attendance(
            attendance_id=attendance_id,
        )

    async def get_by_employee_and_date(
        self,
        employee_id: int,
        tracking_date: date,
    ) -> list[EmployeeTrackingResponse]:

        tracking_list = (
            await self.tracking_repository.get_by_employee_and_date(
                employee_id=employee_id,
                tracking_date=tracking_date,
            )
        )

        return [
            EmployeeTrackingResponse(
                id=tracking.id,
                client_record_id=tracking.client_record_id,
                employee_id=tracking.employee_id,
                employee_name=(
                    f"{tracking.employee.first_name} "
                    f"{tracking.employee.last_name}"
                ),
                attendance_id=tracking.attendance_id,
                recorded_at=tracking.recorded_at,
                latitude=float(tracking.latitude),
                longitude=float(tracking.longitude),
                battery_percentage=tracking.battery_percentage,
            )
            for tracking in tracking_list
        ]