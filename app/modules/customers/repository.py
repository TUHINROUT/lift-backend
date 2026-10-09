from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.models import Customer


class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(
        self,
        email: str,
    ) -> Customer | None:
        stmt = select(Customer).where(
            Customer.email == email
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        project_name: str,
    ) -> Customer | None:
        stmt = select(Customer).where(
            Customer.project_name == project_name
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_last_customer(self) -> Customer | None:
        stmt = (
            select(Customer)
            .order_by(Customer.id.desc())
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Create customer
    async def create(
        self,
        customer: Customer,
    ) -> Customer:
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    # Get all active customers
    async def get_all(self) -> list[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.is_active == True)
            .order_by(Customer.project_name)
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    # Get customer by ID
    async def get_by_id(
        self,
        customer_id: int,
    ) -> Customer | None:
        stmt = select(Customer).where(
            Customer.id == customer_id
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Update customer
    async def update(
        self,
        customer: Customer,
    ) -> Customer:
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    # Activate customer
    async def activate(
        self,
        customer: Customer,
    ) -> Customer:
        customer.is_active = True
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    # Deactivate customer
    async def deactivate(
        self,
        customer: Customer,
    ) -> Customer:
        customer.is_active = False
        await self.db.commit()
        await self.db.refresh(customer)
        return customer


    # Delete customer permanently
    async def delete(
        self,
        customer: Customer,
    ) -> None:
        await self.db.delete(customer)
        await self.db.commit()