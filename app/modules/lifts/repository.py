from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.lifts.models import Lift


class LiftRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_lift_code(
        self,
        lift_code: str,
    ) -> Lift | None:
        stmt = select(Lift).where(
            Lift.lift_code == lift_code
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Create lift
    async def create(
        self,
        lift: Lift,
    ) -> Lift:
        self.db.add(lift)

        await self.db.flush()

        lift_id = lift.id

        await self.db.commit()

        stmt = (
            select(Lift)
            .options(selectinload(Lift.customer))
            .where(Lift.id == lift_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()

    # Get all active lifts
    async def get_all(self) -> list[Lift]:
        stmt = (
            select(Lift)
            .options(selectinload(Lift.customer))
            .where(Lift.is_active == True)
            .order_by(Lift.lift_code)
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    # Get lift by ID
    async def get_by_id(
        self,
        lift_id: int,
    ) -> Lift | None:
        stmt = (
            select(Lift)
            .options(selectinload(Lift.customer))
            .where(Lift.id == lift_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Update lift
    async def update(
        self,
        lift: Lift,
    ) -> Lift:
        await self.db.commit()
        await self.db.refresh(lift)

        return lift

    # Activate lift
    async def activate(
        self,
        lift: Lift,
    ) -> Lift:
        lift.is_active = True

        await self.db.commit()
        await self.db.refresh(lift)

        return lift

    # Deactivate lift
    async def deactivate(
        self,
        lift: Lift,
    ) -> Lift:
        lift.is_active = False

        await self.db.commit()
        await self.db.refresh(lift)

        return lift