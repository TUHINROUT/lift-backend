from datetime import date
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.modules.attendance.schemas import (
    AttendanceResponse,
    AttendanceTrackingResponse,
    AttendanceTrackingSummaryResponse,
    PunchInRequest,
    PunchOutRequest,
)
from app.modules.attendance.service import AttendanceService
from app.modules.users.models import User

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)


@router.post(
    "/punch-in",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/punch-in/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
)
async def punch_in(
    request: PunchInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    try:
        return await service.punch_in(
            user_id=current_user.id,
            latitude=request.latitude,
            longitude=request.longitude,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/punch-out",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
)
@router.post(
    "/punch-out/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
)
async def punch_out(
    request: PunchOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    try:
        return await service.punch_out(
            user_id=current_user.id,
            latitude=request.latitude,
            longitude=request.longitude,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/today",
    response_model=Optional[AttendanceResponse],
)
@router.get(
    "/today/",
    response_model=Optional[AttendanceResponse],
)
async def get_today_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    return await service.get_today(
        user_id=current_user.id,
    )


@router.get(
    "/my",
    response_model=List[AttendanceResponse],
)
@router.get(
    "/my/",
    response_model=List[AttendanceResponse],
)
async def get_my_attendance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AttendanceService(db)
    return await service.get_my_attendance(
        user_id=current_user.id,
    )


@router.get(
    "/tracking",
    response_model=AttendanceTrackingSummaryResponse,
)
@router.get(
    "/tracking/",
    response_model=AttendanceTrackingSummaryResponse,
)
async def get_attendance_tracking(
    attendance_date: Optional[date] = Query(
        None,
        alias="date",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = AttendanceService(db)
    return await service.get_attendance_tracking_summary(
        attendance_date=attendance_date,
    )


@router.get(
    "",
    response_model=List[AttendanceTrackingResponse],
)
@router.get(
    "/",
    response_model=List[AttendanceTrackingResponse],
)
async def get_all_attendance(
    attendance_date: Optional[date] = Query(
        None,
        alias="date",
    ),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = AttendanceService(db)
    try:
        return await service.get_attendance_tracking(
            attendance_date=attendance_date,
            status_filter=status_filter,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )