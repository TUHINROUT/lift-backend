from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.roles.models import Role
from app.modules.roles.repository import RoleRepository
from app.modules.roles.schemas import (
    RoleCreate,
    RoleUpdate,
)


class RoleService:
    def __init__(self, db: AsyncSession):
        self.repository = RoleRepository(db)

    async def create_role(
        self,
        role_data: RoleCreate,
    ) -> Role:

        existing_role = await self.repository.get_by_name(
            role_data.name
        )

        if existing_role:
            raise ValueError("Role already exists.")

        last_role = await self.repository.get_last_role()

        if last_role is None:
            next_number = 1
        else:
            last_code = last_role.role_code
            next_number = int(last_code.replace("ROL", "")) + 1

        role_code = f"ROL{next_number:06d}"

        role = Role(
            role_code=role_code,
            name=role_data.name,
            description=role_data.description,
        )

        return await self.repository.create(role)

    async def get_roles(self) -> list[Role]:
        return await self.repository.get_all()

    async def get_role_by_id(
        self,
        role_id: int,
    ) -> Role:

        role = await self.repository.get_by_id(role_id)

        if role is None:
            raise ValueError("Role not found.")

        return role

    async def update_role(
        self,
        role_id: int,
        role_data: RoleUpdate,
    ) -> Role:

        role = await self.repository.get_by_id(role_id)

        if role is None:
            raise ValueError("Role not found.")

        if (
            role_data.name
            and role_data.name != role.name
        ):
            existing_role = await self.repository.get_by_name(
                role_data.name
            )

            if existing_role:
                raise ValueError("Role already exists.")

            role.name = role_data.name

        if role_data.description is not None:
            role.description = role_data.description

        return await self.repository.update(role)

    async def activate_role(
        self,
        role_id: int,
    ) -> Role:

        role = await self.repository.get_by_id(role_id)

        if role is None:
            raise ValueError("Role not found.")

        return await self.repository.activate(role)

    async def deactivate_role(
        self,
        role_id: int,
    ) -> Role:

        role = await self.repository.get_by_id(role_id)

        if role is None:
            raise ValueError("Role not found.")

        return await self.repository.deactivate(role)