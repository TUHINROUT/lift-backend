from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.departments.models import Department
from app.modules.departments.repository import DepartmentRepository
from app.modules.departments.schemas import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.repository = DepartmentRepository(db)

    async def create_department(self, department_data: DepartmentCreate) -> Department:
        existing_department = await self.repository.get_by_name(department_data.name)
        if existing_department:
            raise ValueError("Department already exists.")

        last_department = await self.repository.get_last_department()
        if last_department is None:
            next_number = 1
        else:
            last_code = last_department.department_code
            next_number = int(last_code.replace("DEP", "")) + 1

        department_code = f"DEP{next_number:06d}"

        department = Department(
            department_code=department_code,
            name=department_data.name,
            description=department_data.description,
        )

        return await self.repository.create(department)

    async def get_departments(self, is_active: bool | None = None) -> list[Department]:
        return await self.repository.get_all(is_active=is_active)

    async def get_department_by_id(self, department_id: int) -> Department:
        department = await self.repository.get_by_id(department_id)
        if department is None:
            raise ValueError("Department not found.")
        return department

    async def update_department(
        self, department_id: int, department_data: DepartmentUpdate
    ) -> Department:
        department = await self.repository.get_by_id(department_id)
        if department is None:
            raise ValueError("Department not found.")

        if (
            department_data.name
            and department_data.name != department.name
        ):
            existing_department = await self.repository.get_by_name(
                department_data.name
            )
            if existing_department:
                raise ValueError("Department already exists.")
            department.name = department_data.name

        if department_data.description is not None:
            department.description = department_data.description

        return await self.repository.update(department)

    async def toggle_department(self, department_id: int) -> Department:
        department = await self.repository.get_by_id(department_id)
        if department is None:
            raise ValueError("Department not found.")
        return await self.repository.toggle_status(department)

    async def activate_department(self, department_id: int) -> Department:
        department = await self.repository.get_by_id(department_id)
        if department is None:
            raise ValueError("Department not found.")
        return await self.repository.activate(department)

    async def deactivate_department(self, department_id: int) -> Department:
        department = await self.repository.get_by_id(department_id)
        if department is None:
            raise ValueError("Department not found.")
        return await self.repository.deactivate(department)

    async def delete_department(self, department_id: int) -> None:
        department = await self.repository.get_by_id(department_id)
        if department is None:
            raise ValueError("Department not found.")
        await self.repository.hard_delete(department)