from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales_visits.models import SalesVisit


class SalesVisitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        sales_visit: SalesVisit,
    ) -> SalesVisit:
        self.db.add(sales_visit)
        await self.db.flush()
        await self.db.refresh(sales_visit)

        return sales_visit

    async def get_by_id(
        self,
        sales_visit_id: int,
    ) -> SalesVisit | None:
        result = await self.db.execute(
            select(SalesVisit).where(
                SalesVisit.id == sales_visit_id,
                SalesVisit.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def get_by_report_number(
        self,
        report_number: str,
    ) -> SalesVisit | None:
        result = await self.db.execute(
            select(SalesVisit).where(
                SalesVisit.report_number == report_number,
                SalesVisit.is_active.is_(True),
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[SalesVisit]:
        result = await self.db.execute(
            select(SalesVisit)
            .where(SalesVisit.is_active.is_(True))
            .order_by(SalesVisit.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[SalesVisit]:
        result = await self.db.execute(
            select(SalesVisit)
            .where(
                SalesVisit.created_by == user_id,
                SalesVisit.is_active.is_(True),
            )
            .order_by(SalesVisit.created_at.desc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        sales_visit: SalesVisit,
        data: dict,
    ) -> SalesVisit:
        for field, value in data.items():
            setattr(sales_visit, field, value)

        await self.db.flush()
        await self.db.refresh(sales_visit)

        return sales_visit

    async def delete(
        self,
        sales_visit: SalesVisit,
    ) -> None:
        sales_visit.is_active = False

        await self.db.flush()