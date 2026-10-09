from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.tickets.models import Ticket


class TicketRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Get ticket by ticket number
    async def get_by_ticket_number(
        self,
        ticket_number: str,
    ) -> Ticket | None:
        stmt = (
            select(Ticket)
            .where(Ticket.ticket_number == ticket_number)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Create ticket
    async def create(
        self,
        ticket: Ticket,
    ) -> Ticket:
        self.db.add(ticket)

        await self.db.flush()

        ticket_id = ticket.id

        await self.db.commit()

        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.lift),
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.closed_by_user),
            )
            .where(Ticket.id == ticket_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()

    # Get all active tickets
    async def get_all(
        self,
    ) -> list[Ticket]:
        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.lift),
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.closed_by_user),
            )
            .where(Ticket.is_active == True)
            .order_by(Ticket.ticket_number)
        )

        result = await self.db.execute(stmt)

        return list(result.scalars().all())

    # Get ticket by ID
    async def get_by_id(
        self,
        ticket_id: int,
    ) -> Ticket | None:
        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.lift),
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.closed_by_user),
            )
            .where(Ticket.id == ticket_id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    # Update ticket
    async def update(
        self,
        ticket: Ticket,
    ) -> Ticket:
        await self.db.commit()

        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.lift),
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.closed_by_user),
            )
            .where(Ticket.id == ticket.id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()

    # Activate ticket
    async def activate(
        self,
        ticket: Ticket,
    ) -> Ticket:
        ticket.is_active = True

        await self.db.commit()

        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.lift),
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.closed_by_user),
            )
            .where(Ticket.id == ticket.id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()

    # Deactivate ticket
    async def deactivate(
        self,
        ticket: Ticket,
    ) -> Ticket:
        ticket.is_active = False

        await self.db.commit()

        stmt = (
            select(Ticket)
            .options(
                selectinload(Ticket.customer),
                selectinload(Ticket.lift),
                selectinload(Ticket.created_by_user),
                selectinload(Ticket.closed_by_user),
            )
            .where(Ticket.id == ticket.id)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one()