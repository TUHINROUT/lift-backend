from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.designations.schemas import (
    DesignationCreate,
    DesignationResponse,
    DesignationUpdate,
)
from app.modules.designations.service import DesignationService
from app.modules.users.models import User

router = APIRouter(
    prefix="/designations",
    tags=["Designations"],
)


#! Create designation
@router.post("", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
async def create_designation(
    request: DesignationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        return await service.create_designation(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Get all designations (supports ?is_active=true filter)
@router.get("", response_model=list[DesignationResponse])
async def get_designations(
    is_active: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)
    return await service.get_designations(is_active=is_active)


#! Get designation by ID
@router.get("/{designation_id}", response_model=DesignationResponse)
async def get_designation(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        return await service.get_designation_by_id(designation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Update designation
@router.put("/{designation_id}", response_model=DesignationResponse)
async def update_designation(
    designation_id: int,
    request: DesignationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        return await service.update_designation(designation_id, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Toggle designation status
@router.patch("/{designation_id}/toggle-status", response_model=DesignationResponse)
async def toggle_designation_status(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        return await service.toggle_designation(designation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Activate designation
@router.patch("/{designation_id}/activate", response_model=DesignationResponse)
async def activate_designation(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        return await service.activate_designation(designation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Deactivate designation
@router.patch("/{designation_id}/deactivate", response_model=DesignationResponse)
async def deactivate_designation(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        return await service.deactivate_designation(designation_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Hard delete designation
@router.delete("/{designation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_designation(
    designation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DesignationService(db)

    try:
        await service.delete_designation(designation_id)
        return None
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )