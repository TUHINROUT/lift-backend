from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.departments.models import Department
from app.modules.designations.models import Designation
from app.modules.users.models import User


class DepartmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> Department | None:
        stmt = select(Department).where(Department.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_department(self) -> Department | None:
        stmt = select(Department).order_by(Department.id.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # Create department
    async def create(self, department: Department) -> Department:
        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)
        return department

    # Get all departments (supports optional is_active filter)
    async def get_all(self, is_active: bool | None = None) -> list[Department]:
        stmt = select(Department).order_by(Department.name)
        if is_active is not None:
            stmt = stmt.where(Department.is_active == is_active)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # Get department by ID
    async def get_by_id(self, department_id: int) -> Department | None:
        stmt = select(Department).where(Department.id == department_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # Update department
    async def update(self, department: Department) -> Department:
        await self.db.commit()
        await self.db.refresh(department)
        return department

    # Toggle status
    async def toggle_status(self, department: Department) -> Department:
        department.is_active = not department.is_active
        await self.db.commit()
        await self.db.refresh(department)
        return department

    # Activate
    async def activate(self, department: Department) -> Department:
        department.is_active = True
        await self.db.commit()
        await self.db.refresh(department)
        return department

    # Deactivate
    async def deactivate(self, department: Department) -> Department:
        department.is_active = False
        await self.db.commit()
        await self.db.refresh(department)
        return department

    # Safe hard delete (unlinks users and designations before deleting)
    async def hard_delete(self, department: Department) -> bool:
        # 1. Unlink users assigned to this department
        await self.db.execute(
            update(User)
            .where(User.department_id == department.id)
            .values(department_id=None)
        )

        # 2. Unlink designations assigned to this department
        await self.db.execute(
            update(Designation)
            .where(Designation.department_id == department.id)
            .values(department_id=None)
        )

        # 3. Safely delete record
        await self.db.delete(department)
        await self.db.commit()
        return True