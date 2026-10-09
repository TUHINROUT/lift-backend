from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import LiftPhase
from app.modules.lift_phases.models import LiftPhaseHistory


class LiftPhaseRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_lift_and_phase(
        self,
        lift_id: int,
        phase: LiftPhase,
    ) -> LiftPhaseHistory | None:

        stmt = (
            select(LiftPhaseHistory)
            .where(
                LiftPhaseHistory.lift_id == lift_id,
                LiftPhaseHistory.phase == phase,
            )
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    
    async def get_by_lift(
        self,
        lift_id: int,
    ) -> list[LiftPhaseHistory]:

        stmt = (
            select(LiftPhaseHistory)
            .where(
                LiftPhaseHistory.lift_id == lift_id,
            )
            .order_by(
                LiftPhaseHistory.completed_at
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    

    async def create(
        self,
        history: LiftPhaseHistory,
    ) -> LiftPhaseHistory:

        self.db.add(history)

        await self.db.commit()

        await self.db.refresh(history)

        return history

    async def get_current_phase(
        self,
        lift_id: int,
    ) -> LiftPhase | None:

        lift = await self.lift_repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        history = await self.repository.get_by_lift(lift_id)

        completed_phases = {
            item.phase
            for item in history
        }

        if LiftPhase.CONSULTATION not in completed_phases:
            return LiftPhase.CONSULTATION

        if LiftPhase.SITE_VISIT not in completed_phases:
            return LiftPhase.SITE_VISIT

        if LiftPhase.HANDOVER not in completed_phases:
            return LiftPhase.HANDOVER

        return None