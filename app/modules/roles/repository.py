from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.roles.models import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(
        self,
        name: str,
    ) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_role(
        self,
    ) -> Role | None:
        stmt = (
            select(Role)
            .order_by(Role.id.desc())
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def create(
        self,
        role: Role,
    ) -> Role:
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_all(
        self,
    ) -> list[Role]:
        stmt = (
            select(Role)
            .where(
                Role.is_active == True,
                Role.name != "ADMIN",
            )
            .order_by(Role.name)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_id(
        self,
        role_id: int,
    ) -> Role | None:
        stmt = select(Role).where(
            Role.id == role_id
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def update(
        self,
        role: Role,
    ) -> Role:
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def activate(
        self,
        role: Role,
    ) -> Role:
        role.is_active = True
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def deactivate(
        self,
        role: Role,
    ) -> Role:
        role.is_active = False
        await self.db.commit()
        await self.db.refresh(role)
        return role