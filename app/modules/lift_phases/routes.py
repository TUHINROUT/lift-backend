from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.lift_phases.schemas import (
    LiftPhaseCompleteRequest,
    LiftPhaseHistoryResponse,
    LiftCurrentPhaseResponse,
)
from app.modules.lift_phases.service import LiftPhaseService
from app.modules.users.models import User


router = APIRouter(
    prefix="/lift-phases",
    tags=["Lift Phases"],
)


@router.post(
    "/{lift_id}/complete",
    response_model=LiftPhaseHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def complete_lift_phase(
    lift_id: int,
    request: LiftPhaseCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = LiftPhaseService(db)

    try:
        return await service.complete_phase(
            lift_id=lift_id,
            phase=request.phase,
            completed_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.get(
    "/{lift_id}/current",
    response_model=LiftCurrentPhaseResponse,
)
async def get_current_lift_phase(
    lift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = LiftPhaseService(db)

    try:
        current_phase = await service.get_current_phase(
            lift_id=lift_id,
        )

        return LiftCurrentPhaseResponse(
            lift_id=lift_id,
            current_phase=current_phase,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )