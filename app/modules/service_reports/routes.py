from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.modules.service_reports.models import CustomerServiceReport
from app.modules.service_reports.schemas import (
    ServiceReportCreate,
    ServiceReportResponse,
)
from app.modules.users.models import User

router = APIRouter(
    prefix="/service-reports",
    tags=["Customer Service Reports"],
)


def parse_date_safely(val: Optional[object]) -> Optional[date]:
    """Converts string dates, datetime objects, or None into a clean Python date object."""
    if not val:
        return date.today()
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        clean_str = str(val).strip().split("T")[0]
        return datetime.strptime(clean_str, "%Y-%m-%d").date()
    except Exception:
        return date.today()


def require_technician_designation(
    current_user: User = Depends(get_current_user),
) -> User:
    """Validates that the logged-in user is a Technician, Service Engineer, or Admin."""
    if current_user.is_superuser:
        return current_user

    designation_name = ""
    if hasattr(current_user, "designation") and current_user.designation:
        designation_name = getattr(current_user.designation, "name", "")
    elif hasattr(current_user, "designation_name"):
        designation_name = current_user.designation_name or ""

    designation_name = str(designation_name).strip().upper()

    allowed = [
        "TECHNICIAN",
        "SERVICE ENGINEER",
        "SENIOR SERVICE ENGINEER",
        "SR. SERVICE ENGINEER",
    ]

    if not any(role in designation_name for role in allowed):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Customer Service Reports are only accessible to Technicians.",
        )
    return current_user


def require_technician_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Allows Technicians to view/edit their reports and Admins/Managers to view all reports on the web dashboard."""
    if current_user.is_superuser:
        return current_user

    role_name = getattr(current_user, "role", None)
    if role_name:
        role_str = getattr(role_name, "name", str(role_name)).upper()
        if "ADMIN" in role_str or "MANAGER" in role_str:
            return current_user

    return require_technician_designation(current_user)


@router.get("/next-sl-no")
async def get_next_serial_number(
    db: AsyncSession = Depends(get_db),
    technician: User = Depends(require_technician_designation),
):
    """Generates the next sequential slip number (e.g. '027') for the mobile form."""
    try:
        query = select(func.count(CustomerServiceReport.id))
        result = await db.execute(query)
        count = result.scalar() or 0
        next_no = f"{count + 1:03d}"
        return {"next_sl_no": next_no}
    except Exception:
        return {"next_sl_no": "001"}


@router.post(
    "",
    response_model=ServiceReportResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=ServiceReportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_report(
    data: ServiceReportCreate,
    db: AsyncSession = Depends(get_db),
    technician: User = Depends(require_technician_designation),
):
    try:
        report_dict = data.model_dump()

        # Sanitize date fields
        report_dict["report_date"] = parse_date_safely(
            report_dict.get("report_date")
        )
        report_dict["call_report_date"] = parse_date_safely(
            report_dict.get("call_report_date")
        )
        report_dict["feedback_date"] = parse_date_safely(
            report_dict.get("feedback_date")
        )

        # Auto slip number if empty
        if not report_dict.get("sl_no"):
            count_query = select(func.count(CustomerServiceReport.id))
            count_res = await db.execute(count_query)
            current_count = count_res.scalar() or 0
            report_dict["sl_no"] = f"{current_count + 1:03d}"

        # Only pass columns that exist on the SQL table
        mapper = inspect(CustomerServiceReport)
        valid_columns = {column.key for column in mapper.attrs}
        filtered_payload = {
            k: v for k, v in report_dict.items() if k in valid_columns
        }
        filtered_payload["technician_id"] = technician.id

        report = CustomerServiceReport(**filtered_payload)
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while saving report: {str(exc)}",
        )


@router.put(
    "/{report_id}",
    response_model=ServiceReportResponse,
)
@router.put(
    "/{report_id}/",
    response_model=ServiceReportResponse,
)
@router.patch(
    "/{report_id}",
    response_model=ServiceReportResponse,
)
@router.patch(
    "/{report_id}/",
    response_model=ServiceReportResponse,
)
async def update_service_report(
    report_id: int,
    data: ServiceReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_technician_or_admin),
):
    """Allows a technician or admin to edit and update an existing Customer Service Report."""
    query = select(CustomerServiceReport).where(
        CustomerServiceReport.id == report_id
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found",
        )

    # Permission check: Technicians can only edit their own reports
    if not user.is_superuser and report.technician_id != user.id:
        role_name = getattr(user, "role", None)
        role_str = (
            getattr(role_name, "name", str(role_name)).upper()
            if role_name
            else ""
        )
        if "ADMIN" not in role_str and "MANAGER" not in role_str:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to edit this report.",
            )

    try:
        update_data = data.model_dump()

        update_data["report_date"] = parse_date_safely(
            update_data.get("report_date")
        )
        update_data["call_report_date"] = parse_date_safely(
            update_data.get("call_report_date")
        )
        update_data["feedback_date"] = parse_date_safely(
            update_data.get("feedback_date")
        )

        mapper = inspect(CustomerServiceReport)
        valid_columns = {column.key for column in mapper.attrs}

        for key, value in update_data.items():
            if key in valid_columns and key not in ["id", "technician_id", "created_at"]:
                setattr(report, key, value)

        report.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(report)
        return report

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update report: {str(exc)}",
        )


@router.get("", response_model=List[ServiceReportResponse])
@router.get("/", response_model=List[ServiceReportResponse])
async def list_service_reports(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_technician_or_admin),
):
    query = select(CustomerServiceReport)

    if not user.is_superuser:
        role_name = getattr(user, "role", None)
        role_str = (
            getattr(role_name, "name", str(role_name)).upper()
            if role_name
            else ""
        )
        if "ADMIN" not in role_str and "MANAGER" not in role_str:
            query = query.where(CustomerServiceReport.technician_id == user.id)

    query = query.order_by(CustomerServiceReport.id.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{report_id}", response_model=ServiceReportResponse)
@router.get("/{report_id}/", response_model=ServiceReportResponse)
async def get_service_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_technician_or_admin),
):
    query = select(CustomerServiceReport).where(
        CustomerServiceReport.id == report_id
    )
    result = await db.execute(query)
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service report not found",
        )

    if not user.is_superuser and report.technician_id != user.id:
        role_name = getattr(user, "role", None)
        role_str = (
            getattr(role_name, "name", str(role_name)).upper()
            if role_name
            else ""
        )
        if "ADMIN" not in role_str and "MANAGER" not in role_str:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this report.",
            )

    return report