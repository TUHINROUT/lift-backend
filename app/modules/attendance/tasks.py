from datetime import datetime, UTC
import app.db.models
from app.core.celery_app import celery_app
from app.db.database import AsyncSessionLocal
from app.modules.attendance.repository import AttendanceRepository


@celery_app.task
def auto_punch_out_open_attendance():
    import asyncio

    return asyncio.run(
        _auto_punch_out_open_attendance()
    )


async def _auto_punch_out_open_attendance():
    async with AsyncSessionLocal() as db:
        repository = AttendanceRepository(db)

        attendance_records = (
            await repository.get_open_attendance()
        )

        now = datetime.now(UTC)

        updated_count = 0

        for attendance in attendance_records:

            if attendance.punch_in_time is None:
                continue

            working_seconds = (
                now - attendance.punch_in_time
            ).total_seconds()

            working_hours = working_seconds / 3600

            attendance.punch_out_time = now

            attendance.punch_out_latitude = (
                attendance.punch_in_latitude
            )

            attendance.punch_out_longitude = (
                attendance.punch_in_longitude
            )

            attendance.working_hours = round(
                working_hours,
                2,
            )

            attendance.status = "AUTO_PUNCH_OUT"

            updated_count += 1

        if updated_count > 0:
            await db.commit()

        return updated_count