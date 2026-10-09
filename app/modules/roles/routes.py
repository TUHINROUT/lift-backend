from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import require_roles
from app.modules.users.models import User
from app.db.session import get_db
from app.modules.roles.schemas import (
    RoleCreate,
    RoleResponse,
)
from app.modules.roles.service import RoleService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


# Create Role
@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    request: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = RoleService(db)

    try:
        return await service.create_role(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# Get All Roles
@router.get(
    "",
    response_model=list[RoleResponse],
)
async def get_roles(
    current_user: User = Depends(require_roles("ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)
    return await service.get_roles()


# Get Role By ID
@router.get(
    "/{role_id}",
    response_model=RoleResponse,
)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = RoleService(db)

    try:
        return await service.get_role_by_id(role_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# Activate Role
@router.patch(
    "/{role_id}/activate",
    response_model=RoleResponse,
)
async def activate_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = RoleService(db)

    try:
        return await service.activate_role(role_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# Deactivate Role
@router.patch(
    "/{role_id}/deactivate",
    response_model=RoleResponse,
)
async def deactivate_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = RoleService(db)

    try:
        return await service.deactivate_role(role_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )