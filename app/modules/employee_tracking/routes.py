from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.employee_tracking.schemas import (
    EmployeeTrackingBatchCreate,
    EmployeeTrackingCreate,
)
from app.modules.employee_tracking.service import EmployeeTrackingService
from app.modules.users.models import User


router = APIRouter(
    prefix="/employee-tracking",
    tags=["Employee Tracking"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_tracking(
    request: EmployeeTrackingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = EmployeeTrackingService(db)

    try:
        return await service.create(
            employee_id=current_user.id,
            data=request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/batch",
    status_code=status.HTTP_201_CREATED,
)
async def create_tracking_batch(
    request: EmployeeTrackingBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = EmployeeTrackingService(db)

    try:
        await service.create_batch(
            employee_id=current_user.id,
            data=request,
        )

        return {
            "message": "Tracking data stored successfully.",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/my",
)
async def get_my_tracking(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("EMPLOYEE")
    ),
):
    service = EmployeeTrackingService(db)

    return await service.get_by_employee(
        employee_id=current_user.id,
    )


@router.get(
    "/employee/{employee_id}",
)
async def get_employee_tracking(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = EmployeeTrackingService(db)
    return await service.get_by_employee(
        employee_id=employee_id,
    )


@router.get(
    "/employee/{employee_id}/latest",
)
async def get_employee_latest_tracking(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = EmployeeTrackingService(db)

    return await service.get_latest_by_employee(
        employee_id=employee_id,
    )


@router.get(
    "/employee/{employee_id}/by-date",
)
async def get_employee_tracking_by_date(
    employee_id: int,
    tracking_date: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = EmployeeTrackingService(db)

    return await service.get_by_employee_and_date(
        employee_id=employee_id,
        tracking_date=tracking_date,
    )