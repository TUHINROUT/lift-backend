from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.designations.models import Designation
from app.modules.designations.repository import DesignationRepository
from app.modules.designations.schemas import (
    DesignationCreate,
    DesignationUpdate,
)


class DesignationService:
    def __init__(self, db: AsyncSession):
        self.repository = DesignationRepository(db)

    async def create_designation(
        self,
        designation_data: DesignationCreate,
    ) -> Designation:
        existing_designation = await self.repository.get_by_name(
            designation_data.name
        )

        if existing_designation:
            raise ValueError("Designation already exists.")

        last_designation = await self.repository.get_last_designation()

        if last_designation is None:
            next_number = 1
        else:
            last_code = last_designation.designation_code
            next_number = int(last_code.replace("DES", "")) + 1

        designation_code = f"DES{next_number:06d}"

        designation = Designation(
            designation_code=designation_code,
            name=designation_data.name,
            description=designation_data.description,
        )

        return await self.repository.create(designation)

    async def get_designations(self, is_active: bool | None = None) -> list[Designation]:
        return await self.repository.get_all(is_active=is_active)

    async def get_designation_by_id(
        self,
        designation_id: int,
    ) -> Designation:
        designation = await self.repository.get_by_id(designation_id)

        if designation is None:
            raise ValueError("Designation not found.")

        return designation

    async def update_designation(
        self,
        designation_id: int,
        designation_data: DesignationUpdate,
    ) -> Designation:
        designation = await self.repository.get_by_id(designation_id)

        if designation is None:
            raise ValueError("Designation not found.")

        if (
            designation_data.name
            and designation_data.name != designation.name
        ):
            existing_designation = await self.repository.get_by_name(
                designation_data.name
            )

            if existing_designation:
                raise ValueError("Designation already exists.")

            designation.name = designation_data.name

        if designation_data.description is not None:
            designation.description = designation_data.description

        return await self.repository.update(designation)

    async def toggle_designation(
        self,
        designation_id: int,
    ) -> Designation:
        designation = await self.repository.get_by_id(designation_id)

        if designation is None:
            raise ValueError("Designation not found.")

        return await self.repository.toggle_status(designation)

    async def activate_designation(
        self,
        designation_id: int,
    ) -> Designation:
        designation = await self.repository.get_by_id(designation_id)

        if designation is None:
            raise ValueError("Designation not found.")

        return await self.repository.activate(designation)

    async def deactivate_designation(
        self,
        designation_id: int,
    ) -> Designation:
        designation = await self.repository.get_by_id(designation_id)

        if designation is None:
            raise ValueError("Designation not found.")

        return await self.repository.deactivate(designation)

    async def delete_designation(
        self,
        designation_id: int,
    ) -> None:
        designation = await self.repository.get_by_id(designation_id)

        if designation is None:
            raise ValueError("Designation not found.")

        await self.repository.hard_delete(designation)