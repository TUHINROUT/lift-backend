from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.models import Customer
from app.modules.customers.repository import CustomerRepository
from app.modules.customers.schemas import (
    CustomerCreate,
    CustomerUpdate,
)


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.repository = CustomerRepository(db)

    async def create_customer(
        self,
        customer_data: CustomerCreate,
    ) -> Customer:

        if customer_data.email:
            existing_customer = await self.repository.get_by_email(
                customer_data.email
            )

            if existing_customer:
                raise ValueError("Customer email already exists.")

        last_customer = await self.repository.get_last_customer()

        if last_customer is None:
            next_number = 1
        else:
            last_code = last_customer.customer_code
            next_number = int(last_code.replace("CUS", "")) + 1

        customer_code = f"CUS{next_number:06d}"

        customer = Customer(
            customer_code=customer_code,
            project_name=customer_data.project_name,
            contact_person=customer_data.contact_person,
            mobile=customer_data.mobile,
            alternate_mobile=customer_data.alternate_mobile,
            email=customer_data.email,
            address=customer_data.address,
            city=customer_data.city,
            state=customer_data.state,
            pincode=customer_data.pincode,
            gst_number=customer_data.gst_number,
            description=customer_data.description,
        )

        return await self.repository.create(customer)

    async def get_customers(self) -> list[Customer]:
        return await self.repository.get_all()

    async def get_customer_by_id(
        self,
        customer_id: int,
    ) -> Customer:
        customer = await self.repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError("Customer not found.")

        return customer

    async def update_customer(
        self,
        customer_id: int,
        customer_data: CustomerUpdate,
    ) -> Customer:

        customer = await self.repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError("Customer not found.")

        if (
            customer_data.email
            and customer_data.email != customer.email
        ):
            existing_customer = await self.repository.get_by_email(
                customer_data.email
            )

            if existing_customer:
                raise ValueError("Customer email already exists.")

            customer.email = customer_data.email

        if customer_data.project_name is not None:
            customer.project_name = customer_data.project_name

        if customer_data.contact_person is not None:
            customer.contact_person = customer_data.contact_person

        if customer_data.mobile is not None:
            customer.mobile = customer_data.mobile

        if customer_data.alternate_mobile is not None:
            customer.alternate_mobile = customer_data.alternate_mobile

        if customer_data.address is not None:
            customer.address = customer_data.address

        if customer_data.city is not None:
            customer.city = customer_data.city

        if customer_data.state is not None:
            customer.state = customer_data.state

        if customer_data.pincode is not None:
            customer.pincode = customer_data.pincode

        if customer_data.gst_number is not None:
            customer.gst_number = customer_data.gst_number

        if customer_data.description is not None:
            customer.description = customer_data.description

        return await self.repository.update(customer)

    async def activate_customer(
        self,
        customer_id: int,
    ) -> Customer:

        customer = await self.repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError("Customer not found.")

        return await self.repository.activate(customer)

    async def deactivate_customer(
        self,
        customer_id: int,
    ) -> Customer:

        customer = await self.repository.get_by_id(customer_id)

        if customer is None:
            raise ValueError("Customer not found.")

        return await self.repository.deactivate(customer)

    async def delete_customer(
            self,
            customer_id: int,
        ) -> None:
    
            customer = await self.repository.get_by_id(customer_id)
    
            if customer is None:
                raise ValueError("Customer not found.")
    
            await self.repository.delete(customer)