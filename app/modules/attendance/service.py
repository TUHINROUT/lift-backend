from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.models import Attendance
from app.modules.attendance.schemas import (
    AttendanceResponse,
    AttendanceTrackingResponse,
    AttendanceTrackingSummaryResponse,
)
from app.modules.attendance.repository import AttendanceRepository
from app.modules.users.repository import UsersRepository


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.repository = AttendanceRepository(db)
        self.user_repository = UsersRepository(db)

    def _to_response(
        self,
        attendance: Attendance,
    ) -> AttendanceResponse:
        user_display_name = ""
        if hasattr(attendance, "user") and attendance.user:
            first_name = attendance.user.first_name or ""
            last_name = attendance.user.last_name or ""
            user_display_name = f"{first_name} {last_name}".strip()

        return AttendanceResponse(
            id=attendance.id,
            user_id=attendance.user_id,
            user_name=user_display_name,
            date=attendance.date,
            punch_in_time=attendance.punch_in_time,
            punch_in_latitude=attendance.punch_in_latitude,
            punch_in_longitude=attendance.punch_in_longitude,
            punch_out_time=attendance.punch_out_time,
            punch_out_latitude=attendance.punch_out_latitude,
            punch_out_longitude=attendance.punch_out_longitude,
            working_hours=attendance.working_hours,
            status=attendance.status,
            created_at=attendance.created_at,
            updated_at=attendance.updated_at,
        )

    async def _validate_attendance_location(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
    ) -> None:
        """
        Validates user existence and permits all staff (Sales, Technicians,
        Engineers, and Office employees) to punch in from any location.
        """
        user = await self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found.")
        # Geofence perimeter check bypassed: punch-in is allowed everywhere.
        return

    async def punch_in(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
    ) -> AttendanceResponse:
        # Use timezone.utc to safely get today's date
        today = datetime.now(timezone.utc).date()

        existing = await self.repository.get_by_user_and_date(
            user_id=user_id,
            attendance_date=today,
        )

        if existing is not None and existing.punch_in_time is not None:
            raise ValueError("Attendance already exists for today.")

        await self._validate_attendance_location(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
        )

        now = datetime.now(timezone.utc)

        if existing is None:
            attendance = Attendance(
                user_id=user_id,
                date=today,
                punch_in_time=now,
                punch_in_latitude=latitude,
                punch_in_longitude=longitude,
                status="PRESENT",
            )
            attendance = await self.repository.create(attendance)
        else:
            existing.punch_in_time = now
            existing.punch_in_latitude = latitude
            existing.punch_in_longitude = longitude
            existing.status = "PRESENT"
            attendance = await self.repository.update(existing)

        return self._to_response(attendance)

    async def punch_out(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
    ) -> AttendanceResponse:
        today = datetime.now(timezone.utc).date()

        attendance = await self.repository.get_by_user_and_date(
            user_id=user_id,
            attendance_date=today,
        )

        if attendance is None or attendance.punch_in_time is None:
            raise ValueError("Punch In is required before Punch Out.")

        if attendance.punch_out_time is not None:
            raise ValueError("Already punched out for today.")

        has_in_progress_task = (
            await self.repository.has_in_progress_task(
                employee_id=user_id,
            )
        )

        if has_in_progress_task:
            raise ValueError("Finish your task before punching out.")

        now = datetime.now(timezone.utc)

        # Calculate working hours safely handling tz-aware or naive datetimes
        punch_in_time = attendance.punch_in_time
        if punch_in_time.tzinfo is None:
            punch_in_time = punch_in_time.replace(tzinfo=timezone.utc)

        working_seconds = (now - punch_in_time).total_seconds()
        working_hours = max(0.0, working_seconds / 3600)

        attendance.punch_out_time = now
        attendance.punch_out_latitude = latitude
        attendance.punch_out_longitude = longitude
        attendance.working_hours = round(working_hours, 2)
        attendance.status = "PRESENT"

        attendance = await self.repository.update(attendance)
        return self._to_response(attendance)

    async def get_today(
        self,
        user_id: int,
    ) -> AttendanceResponse | None:
        today = date.today()
        attendance = await self.repository.get_by_user_and_date(
            user_id=user_id,
            attendance_date=today,
        )
        if attendance is None:
            return None

        return self._to_response(attendance)

    async def get_all(
        self,
    ) -> list[AttendanceResponse]:
        attendance_list = await self.repository.get_all()

        return [
            self._to_response(attendance)
            for attendance in attendance_list
        ]

    async def get_attendance_tracking(
        self,
        attendance_date: date | None = None,
        status_filter: str | None = None,
    ) -> list[AttendanceTrackingResponse]:
        if attendance_date is None:
            attendance_date = datetime.now(timezone.utc).date()

        if status_filter is not None:
            status_filter = status_filter.upper()

            if status_filter not in {"PRESENT", "ABSENT"}:
                raise ValueError("Status must be PRESENT or ABSENT.")

        # Get Active Managers + Employees
        users = await self.repository.get_active_attendance_users()

        # Get Attendance for Selected Date
        attendance_list = await self.repository.get_attendance_by_date(
            attendance_date=attendance_date,
        )

        # Create Attendance Lookup
        attendance_by_user = {
            attendance.user_id: attendance
            for attendance in attendance_list
        }

        tracking_list = []

        for user in users:
            attendance = attendance_by_user.get(user.id)
            employee_status = "PRESENT" if attendance is not None else "ABSENT"

            if (
                status_filter is not None
                and employee_status != status_filter
            ):
                continue

            tracking_list.append(
                AttendanceTrackingResponse(
                    employee_id=user.id,
                    employee_code=user.employee_code,
                    name=f"{user.first_name} {user.last_name}".strip(),
                    department=user.department.name if user.department else None,
                    designation=user.designation.name if user.designation else None,
                    role=user.role.name if user.role else None,
                    date=attendance_date,
                    status=employee_status,
                    punch_in_time=attendance.punch_in_time if attendance else None,
                    punch_in_latitude=attendance.punch_in_latitude if attendance else None,
                    punch_in_longitude=attendance.punch_in_longitude if attendance else None,
                    punch_out_time=attendance.punch_out_time if attendance else None,
                    punch_out_latitude=attendance.punch_out_latitude if attendance else None,
                    punch_out_longitude=attendance.punch_out_longitude if attendance else None,
                    working_hours=(
                        float(attendance.working_hours)
                        if (attendance is not None and attendance.working_hours is not None)
                        else None
                    ),
                )
            )

        return tracking_list

    async def get_attendance_tracking_summary(
        self,
        attendance_date: date | None = None,
    ) -> AttendanceTrackingSummaryResponse:
        if attendance_date is None:
            attendance_date = datetime.now(timezone.utc).date()

        users = await self.repository.get_active_attendance_users()
        attendance_list = await self.repository.get_attendance_by_date(
            attendance_date=attendance_date,
        )

        attendance_by_user = {
            attendance.user_id: attendance
            for attendance in attendance_list
        }

        total_employees = len(users)
        present = sum(1 for user in users if user.id in attendance_by_user)
        absent = total_employees - present

        return AttendanceTrackingSummaryResponse(
            date=attendance_date,
            total_employees=total_employees,
            present=present,
            absent=absent,
        )

    async def get_my_attendance(
        self,
        user_id: int,
    ) -> list[AttendanceResponse]:
        attendance_list = await self.repository.get_by_user(
            user_id=user_id,
        )

        return [
            self._to_response(attendance)
            for attendance in attendance_list
        ]