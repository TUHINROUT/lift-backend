import asyncio

from app.db.database import AsyncSessionLocal
from app.modules.attendance.repository import AttendanceRepository


async def main():
    async with AsyncSessionLocal() as db:
        repository = AttendanceRepository(db)

        rows = await repository.get_open_attendance()

        print("Open attendance count:", len(rows))

        for row in rows:
            print(
                row.id,
                row.user_id,
                row.punch_in_time,
                row.punch_out_time,
                row.punch_in_latitude,
                row.punch_in_longitude,
                row.status,
            )


asyncio.run(main())
