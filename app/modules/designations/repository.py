from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.designations.models import Designation
from app.modules.users.models import User


class DesignationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> Designation | None:
        stmt = select(Designation).where(Designation.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_designation(self) -> Designation | None:
        stmt = (
            select(Designation)
            .order_by(Designation.id.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # Create designation
    async def create(
        self,
        designation: Designation,
    ) -> Designation:
        self.db.add(designation)
        await self.db.commit()
        await self.db.refresh(designation)
        return designation

    # Get designations (supports optional is_active filter)
    async def get_all(self, is_active: bool | None = None) -> list[Designation]:
        stmt = select(Designation).order_by(Designation.name)
        if is_active is not None:
            stmt = stmt.where(Designation.is_active == is_active)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # Get designation by ID
    async def get_by_id(
        self,
        designation_id: int,
    ) -> Designation | None:
        stmt = select(Designation).where(
            Designation.id == designation_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # Update designation
    async def update(
        self,
        designation: Designation,
    ) -> Designation:
        await self.db.commit()
        await self.db.refresh(designation)
        return designation

    # Toggle designation status
    async def toggle_status(
        self,
        designation: Designation,
    ) -> Designation:
        designation.is_active = not designation.is_active
        await self.db.commit()
        await self.db.refresh(designation)
        return designation

    # Activate designation
    async def activate(
        self,
        designation: Designation,
    ) -> Designation:
        designation.is_active = True
        await self.db.commit()
        await self.db.refresh(designation)
        return designation

    # Deactivate designation
    async def deactivate(
        self,
        designation: Designation,
    ) -> Designation:
        designation.is_active = False
        await self.db.commit()
        await self.db.refresh(designation)
        return designation

    # Safe hard delete (unlinks users first to prevent foreign key errors)
    async def hard_delete(
        self,
        designation: Designation,
    ) -> bool:
        # 1. Unlink users assigned to this designation
        await self.db.execute(
            update(User)
            .where(User.designation_id == designation.id)
            .values(designation_id=None)
        )

        # 2. Safely delete the designation
        await self.db.delete(designation)
        await self.db.commit()
        return True