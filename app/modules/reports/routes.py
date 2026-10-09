from pathlib import Path
from typing import Optional
import urllib.parse
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.reports.pdf import generate_lift_report_pdf
from app.modules.reports.schemas import (
    LiftReportResponse,
    MonthlyAttendanceResponse,
)
from app.modules.reports.service import ReportService
from app.modules.users.models import User

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def sanitize_filename_code(code: str) -> str:
    """Replaces filesystem-unsafe characters like / and \\."""
    return code.replace("/", "-").replace("\\", "-").strip()


# ---------------------------------------------------------
# 1. DOWNLOAD LIFT REPORT PDF
# Placed FIRST to prevent path collisions.
# Accepts: GET /reports/pdf/lift?lift_code=JEI/23-24/0865
# ---------------------------------------------------------
@router.get(
    "/pdf/lift",
)
async def get_lift_report_pdf_by_query(
    lift_code: str = Query(..., alias="lift_code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    target_code = urllib.parse.unquote(lift_code).strip()
    if not target_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lift code is required.",
        )

    service = ReportService(db)
    try:
        report = await service.get_lift_report(
            lift_code=target_code,
        )

        output_dir = Path("uploads/reports")
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            output_dir
            / f"lift_report_{uuid4().hex}.pdf"
        )

        generate_lift_report_pdf(
            report=report,
            output_path=output_path,
        )

        safe_name = sanitize_filename_code(target_code)

        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"lift_report_{safe_name}.pdf",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ---------------------------------------------------------
# 2. GET LIFT REPORT (JSON DATA)
# Supports:
#   GET /reports/lift?lift_code=JEI/23-24/0865
#   GET /reports/lift/JEI/23-24/0865
# ---------------------------------------------------------
@router.get(
    "/lift",
    response_model=LiftReportResponse,
)
@router.get(
    "/lift/{lift_code:path}",
    response_model=LiftReportResponse,
)
async def get_lift_report(
    lift_code: Optional[str] = None,
    code_query: Optional[str] = Query(None, alias="lift_code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    target_code = lift_code or code_query
    if not target_code or not target_code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lift code is required.",
        )

    # Clean off trailing /pdf if any client requests it
    target_code = urllib.parse.unquote(target_code).strip()
    if target_code.endswith("/pdf"):
        target_code = target_code[:-4].strip()

    service = ReportService(db)
    try:
        return await service.get_lift_report(
            lift_code=target_code,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ---------------------------------------------------------
# 3. MONTHLY ATTENDANCE REPORT
# ---------------------------------------------------------
@router.get(
    "/attendance/monthly",
    response_model=MonthlyAttendanceResponse,
)
async def get_monthly_attendance_report(
    year: int,
    month: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = ReportService(db)
    try:
        return await service.get_monthly_attendance_report(
            year=year,
            month=month,
            status=status_filter,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )