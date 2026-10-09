from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.departments.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.modules.departments.service import DepartmentService
from app.modules.users.models import User

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


#! Create department post
@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    request: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        return await service.create_department(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Get all departments (pass ?is_active=true for employee dropdowns, or omit to view all)
@router.get("", response_model=list[DepartmentResponse])
async def get_departments(
    is_active: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    return await service.get_departments(is_active=is_active)


#! Get department by department_id
@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        return await service.get_department_by_id(department_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Update department by department_id
@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    request: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        return await service.update_department(department_id, request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Toggle department status
@router.patch("/{department_id}/toggle-status", response_model=DepartmentResponse)
async def toggle_department_status(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        return await service.toggle_department(department_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Activate department
@router.patch("/{department_id}/activate", response_model=DepartmentResponse)
async def activate_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        return await service.activate_department(department_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Deactivate department
@router.patch("/{department_id}/deactivate", response_model=DepartmentResponse)
async def deactivate_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        return await service.deactivate_department(department_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Hard delete department
@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = DepartmentService(db)
    try:
        await service.delete_department(department_id)
        return None
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )