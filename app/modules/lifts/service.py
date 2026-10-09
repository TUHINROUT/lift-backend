from sqlalchemy.ext.asyncio import AsyncSession
from app.services.email import send_email, EmailSendError
from app.modules.customers.repository import CustomerRepository
from app.modules.lifts.models import Lift
from app.modules.lifts.repository import LiftRepository
from app.modules.lifts.schemas import (
    LiftCreate,
    LiftUpdate,
)


class LiftService:
    def __init__(self, db: AsyncSession):
        self.repository = LiftRepository(db)
        self.customer_repository = CustomerRepository(db)

    async def create_lift(
        self,
        lift_data: LiftCreate,
    ) -> Lift:

        existing_lift = await self.repository.get_by_lift_code(
            lift_data.lift_code
        )

        if existing_lift:
            raise ValueError("Lift code already exists.")

        customer = await self.customer_repository.get_by_id(
            lift_data.customer_id
        )

        if customer is None:
            raise ValueError("Customer not found.")

        lift = Lift(
            lift_code=lift_data.lift_code,
            customer_id=lift_data.customer_id,
            building_name=lift_data.building_name,
            address=lift_data.address,
            latitude=lift_data.latitude,
            longitude=lift_data.longitude,
            installation_date=lift_data.installation_date,
            warranty=lift_data.warranty,
            amc=lift_data.amc,
            status=lift_data.status,
            capacity=lift_data.capacity,
            lift_type=lift_data.lift_type,
            machine_type=lift_data.machine_type,
            controller_type=lift_data.controller_type,
            door_type=lift_data.door_type,
            stops=lift_data.stops,
            floors=lift_data.floors,
            manufacturer=lift_data.manufacturer,
            serial_number=lift_data.serial_number,
            drawing=lift_data.drawing,
            remarks=lift_data.remarks,
        )

        created_lift = await self.repository.create(lift)

        if customer.email:
            subject = f"Lift Details - {created_lift.lift_code}"
            body = f"""
        Dear {customer.contact_person or customer.project_name},

        A lift has been successfully assigned..
        LIFT DETAILS
        ==============================
        Lift Code: {created_lift.lift_code}
        Customer Code: {customer.customer_code}
        Project Name: {customer.project_name}

        Building Name: {created_lift.building_name}
        Address: {created_lift.address}

        Installation Date: {created_lift.installation_date or "Not Available"}
        Warranty: {created_lift.warranty or "Not Available"}
        AMC: {created_lift.amc or "Not Available"}
        Lift Status: {created_lift.status or "Not Available"}

        Capacity: {created_lift.capacity or "Not Available"}
        Lift Type: {created_lift.lift_type or "Not Available"}
        Machine Type: {created_lift.machine_type or "Not Available"}
        Controller Type: {created_lift.controller_type or "Not Available"}
        Door Type: {created_lift.door_type or "Not Available"}

        Number of Stops: {created_lift.stops or "Not Available"}
        Number of Floors: {created_lift.floors or "Not Available"}

        Manufacturer: {created_lift.manufacturer or "Not Available"}
        Serial Number: {created_lift.serial_number or "Not Available"}

        Remarks:
        {created_lift.remarks or "No remarks"}
        ==============================
        Thank you,
        Evio Elevator.
        """
            try:
                send_email(
                    to_email=customer.email,
                    subject=subject,
                    body=body,
                )

            except EmailSendError as exc:
                # The lift is already successfully created.
                # We don't want an email failure to roll back the lift creation.
                print(
                    f"Failed to send lift details email "
                    f"to {customer.email}: {exc}"
                )
        return created_lift

    async def get_lifts(self) -> list[Lift]:
        return await self.repository.get_all()

    async def get_lift_by_id(
        self,
        lift_id: int,
    ) -> Lift:

        lift = await self.repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        return lift

    async def update_lift(
        self,
        lift_id: int,
        lift_data: LiftUpdate,
    ) -> Lift:

        lift = await self.repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        if lift_data.building_name is not None:
            lift.building_name = lift_data.building_name

        if lift_data.address is not None:
            lift.address = lift_data.address

        if lift_data.latitude is not None:
            lift.latitude = lift_data.latitude

        if lift_data.longitude is not None:
            lift.longitude = lift_data.longitude

        if lift_data.installation_date is not None:
            lift.installation_date = lift_data.installation_date

        if lift_data.warranty is not None:
            lift.warranty = lift_data.warranty

        if lift_data.amc is not None:
            lift.amc = lift_data.amc

        if lift_data.status is not None:
            lift.status = lift_data.status

        if lift_data.capacity is not None:
            lift.capacity = lift_data.capacity

        if lift_data.lift_type is not None:
            lift.lift_type = lift_data.lift_type

        if lift_data.machine_type is not None:
            lift.machine_type = lift_data.machine_type

        if lift_data.controller_type is not None:
            lift.controller_type = lift_data.controller_type

        if lift_data.door_type is not None:
            lift.door_type = lift_data.door_type

        if lift_data.stops is not None:
            lift.stops = lift_data.stops

        if lift_data.floors is not None:
            lift.floors = lift_data.floors

        if lift_data.manufacturer is not None:
            lift.manufacturer = lift_data.manufacturer

        if lift_data.serial_number is not None:
            lift.serial_number = lift_data.serial_number

        if lift_data.drawing is not None:
            lift.drawing = lift_data.drawing

        if lift_data.remarks is not None:
            lift.remarks = lift_data.remarks

        return await self.repository.update(lift)

    async def activate_lift(
        self,
        lift_id: int,
    ) -> Lift:

        lift = await self.repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        return await self.repository.activate(lift)

    async def deactivate_lift(
        self,
        lift_id: int,
    ) -> Lift:

        lift = await self.repository.get_by_id(lift_id)

        if lift is None:
            raise ValueError("Lift not found.")

        return await self.repository.deactivate(lift)