from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import TicketStatus
from app.modules.customers.repository import CustomerRepository
from app.modules.lifts.repository import LiftRepository
from app.modules.tickets.models import Ticket
from app.modules.tickets.repository import TicketRepository
from app.modules.tickets.schemas import (
    TicketCreate,
    TicketUpdate,
)
from app.modules.users.repository import UsersRepository


class TicketService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repository = TicketRepository(db)

        self.customer_repository = CustomerRepository(db)

        self.lift_repository = LiftRepository(db)

        self.user_repository = UsersRepository(db)


    async def create_ticket(
            self,
            ticket_data: TicketCreate,
            created_by: int,
        ) -> Ticket:

            # Check ticket number uniqueness
            existing_ticket = await self.repository.get_by_ticket_number(
                ticket_data.ticket_number
            )

            if existing_ticket is not None:
                raise ValueError("Ticket number already exists.")

            # Validate customer
            customer = await self.customer_repository.get_by_id(
                ticket_data.customer_id
            )

            if customer is None:
                raise ValueError("Customer not found.")

            # Validate lift
            lift = await self.lift_repository.get_by_id(
                ticket_data.lift_id
            )

            if lift is None:
                raise ValueError("Lift not found.")

            # Validate lift belongs to customer
            if lift.customer_id != ticket_data.customer_id:
                raise ValueError(
                    "Selected lift does not belong to the selected customer."
                )

            # Validate manager/admin user
            user = await self.user_repository.get_user_by_id(
                created_by
            )

            if user is None:
                raise ValueError("User not found.")

            # Create ticket
            ticket = Ticket(
                ticket_number=ticket_data.ticket_number,
                customer_id=ticket_data.customer_id,
                contact_person=ticket_data.contact_person,
                contact_number=ticket_data.contact_number,
                lift_id=ticket_data.lift_id,
                ticket_type=ticket_data.ticket_type,
                priority=ticket_data.priority,
                complaint_description=ticket_data.complaint_description,
                status=TicketStatus.OPEN,
                created_by=created_by,
            )

            return await self.repository.create(ticket)



    async def get_tickets(
                self,
            ) -> list[Ticket]:

                return await self.repository.get_all()

    async def get_ticket_by_id(
                self,
                ticket_id: int,
            ) -> Ticket:

                ticket = await self.repository.get_by_id(
                    ticket_id
                )

                if ticket is None:
                    raise ValueError("Ticket not found.")

                return ticket

    async def update_ticket(
            self,
            ticket_id: int,
            ticket_data: TicketUpdate,
        ) -> Ticket:

            ticket = await self.repository.get_by_id(ticket_id)

            if ticket is None:
                raise ValueError("Ticket not found.")

            # Validate customer
            if ticket_data.customer_id is not None:

                customer = await self.customer_repository.get_by_id(
                    ticket_data.customer_id
                )

                if customer is None:
                    raise ValueError("Customer not found.")

                ticket.customer_id = ticket_data.customer_id
                lift = await self.lift_repository.get_by_id(
                    ticket.lift_id
                )
                if lift is None:
                    raise ValueError("Lift not found.")

                if lift.customer_id != ticket.customer_id:
                    raise ValueError(
                        "Selected lift does not belong to the selected customer."
                    )

            # Validate lift
            if ticket_data.lift_id is not None:

                lift = await self.lift_repository.get_by_id(
                    ticket_data.lift_id
                )

                if lift is None:
                    raise ValueError("Lift not found.")

                expected_customer_id = (
                    ticket_data.customer_id
                    if ticket_data.customer_id is not None
                    else ticket.customer_id
                )

                if lift.customer_id != expected_customer_id:
                    raise ValueError(
                        "Selected lift does not belong to the selected customer."
                    )

                ticket.lift_id = ticket_data.lift_id

            if ticket_data.contact_person is not None:
                ticket.contact_person = ticket_data.contact_person

            if ticket_data.contact_number is not None:
                ticket.contact_number = ticket_data.contact_number

            if ticket_data.ticket_type is not None:
                ticket.ticket_type = ticket_data.ticket_type

            if ticket_data.priority is not None:
                ticket.priority = ticket_data.priority

            if ticket_data.complaint_description is not None:
                ticket.complaint_description = (
                    ticket_data.complaint_description
                )

            if ticket_data.status is not None:
                ticket.status = ticket_data.status

            if ticket_data.closing_remarks is not None:
                ticket.closing_remarks = ticket_data.closing_remarks

            return await self.repository.update(ticket)

    async def activate_ticket(
        self,
        ticket_id: int,
    ) -> Ticket:

        ticket = await self.repository.get_by_id(
            ticket_id
        )

        if ticket is None:
            raise ValueError("Ticket not found.")

        return await self.repository.activate(ticket)

    async def deactivate_ticket(
        self,
        ticket_id: int,
    ) -> Ticket:

        ticket = await self.repository.get_by_id(
            ticket_id
        )

        if ticket is None:
            raise ValueError("Ticket not found.")

        return await self.repository.deactivate(ticket)


    async def close_ticket(
        self,
        ticket_id: int,
        closing_remarks: str,
        closed_by: int,
    ) -> Ticket:

        ticket = await self.repository.get_by_id(
            ticket_id
        )

        if ticket is None:
            raise ValueError("Ticket not found.")

        user = await self.user_repository.get_user_by_id(
            closed_by
        )

        if user is None:
            raise ValueError("User not found.")

        if ticket.status == TicketStatus.CLOSED:
            raise ValueError("Ticket is already closed.")

        if not closing_remarks.strip():
            raise ValueError("Closing remarks are required.")

        ticket.status = TicketStatus.CLOSED
        ticket.closed_by = closed_by
        ticket.closed_at = datetime.now(UTC)
        ticket.closing_remarks = closing_remarks
        
        return await self.repository.update(ticket)