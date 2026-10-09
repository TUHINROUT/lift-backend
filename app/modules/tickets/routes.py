from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.tickets.schemas import (
    TicketClose,
    TicketCreate,
    TicketResponse,
    TicketUpdate,
)
from app.modules.tickets.service import TicketService
from app.modules.users.models import User

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)

#! Create Ticket
@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    request: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    try:
        return await service.create_ticket(
            request,
            created_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

#! Get All Tickets
@router.get(
    "",
    response_model=list[TicketResponse],
)
async def get_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    return await service.get_tickets()


#! Get Ticket By ID
@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    try:
        return await service.get_ticket_by_id(ticket_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Update Ticket
@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
)
async def update_ticket(
    ticket_id: int,
    request: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    try:
        return await service.update_ticket(
            ticket_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

#! Activate Ticket
@router.patch(
    "/{ticket_id}/activate",
    response_model=TicketResponse,
)
async def activate_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    try:
        return await service.activate_ticket(ticket_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

#! Deactivate Ticket
@router.patch(
    "/{ticket_id}/deactivate",
    response_model=TicketResponse,
)
async def deactivate_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    try:
        return await service.deactivate_ticket(ticket_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

#! Close Ticket
@router.patch(
    "/{ticket_id}/close",
    response_model=TicketResponse,
)
async def close_ticket(
    ticket_id: int,
    request: TicketClose,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = TicketService(db)

    try:
        return await service.close_ticket(
            ticket_id=ticket_id,
            closing_remarks=request.closing_remarks,
            closed_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )