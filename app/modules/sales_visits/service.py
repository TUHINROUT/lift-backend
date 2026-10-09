from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales_visits.models import SalesVisit
from app.modules.sales_visits.repository import SalesVisitRepository
from app.modules.sales_visits.schemas import (
    SalesVisitCreate,
    SalesVisitUpdate,
)


class SalesVisitService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SalesVisitRepository(db)

    async def create(
        self,
        data: SalesVisitCreate,
        user_id: int,
    ) -> SalesVisit:

        report_number = f"SR-{uuid4().hex[:8].upper()}"

        sales_visit = SalesVisit(
            report_number=report_number,
            created_by=user_id,
            client_name=data.client_name,
            contact_person=data.contact_person,
            phone=data.phone,
            location=data.location,
            lift_type=data.lift_type,
            units=data.units,
            estimated_quote=data.estimated_quote,
            visit_date=data.visit_date,
            visit_time=data.visit_time,
            status=data.status or "New Lead",
            notes=data.notes,
            site_image=data.site_image,
        )

        try:
            sales_visit = await self.repository.create(sales_visit)

            await self.db.commit()

            await self.db.refresh(sales_visit)

            return sales_visit

        except Exception:
            await self.db.rollback()
            raise

    async def get_by_id(
        self,
        sales_visit_id: int,
    ) -> SalesVisit | None:

        return await self.repository.get_by_id(
            sales_visit_id
        )

    async def get_all(self) -> list[SalesVisit]:

        return await self.repository.get_all()

    async def get_by_user(
        self,
        user_id: int,
    ) -> list[SalesVisit]:

        return await self.repository.get_by_user(
            user_id
        )

    async def update(
        self,
        sales_visit_id: int,
        data: SalesVisitUpdate,
    ) -> SalesVisit | None:

        sales_visit = await self.repository.get_by_id(
            sales_visit_id
        )

        if not sales_visit:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        try:
            sales_visit = await self.repository.update(
                sales_visit,
                update_data,
            )

            await self.db.commit()

            await self.db.refresh(sales_visit)

            return sales_visit

        except Exception:
            await self.db.rollback()
            raise

    async def delete(
        self,
        sales_visit_id: int,
    ) -> bool:

        sales_visit = await self.repository.get_by_id(
            sales_visit_id
        )

        if not sales_visit:
            return False

        try:
            await self.repository.delete(
                sales_visit
            )

            await self.db.commit()

            return True

        except Exception:
            await self.db.rollback()
            raise