from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_roles
from app.db.session import get_db
from app.modules.sales_visits.models import SalesVisit
from app.modules.sales_visits.schemas import (
    SalesVisitCreate,
    SalesVisitResponse,
    SalesVisitUpdate,
)
from app.modules.sales_visits.service import SalesVisitService
from app.modules.users.models import User

router = APIRouter(
    prefix="/sales-visits",
    tags=["Sales Visits"],
)


def parse_date_safely(val: Optional[object]) -> date:
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


def parse_time_safely(val: Optional[object]) -> time:
    if not val:
        return datetime.utcnow().time()
    if isinstance(val, time):
        return val
    try:
        clean_str = str(val).strip()
        parts = clean_str.split(":")
        return time(
            int(parts[0]),
            int(parts[1]),
            int(float(parts[2])) if len(parts) > 2 else 0,
        )
    except Exception:
        return datetime.utcnow().time()


def get_user_column_name() -> str:
    """Dynamically determines the user ownership column on the model."""
    mapper = inspect(SalesVisit)
    valid_cols = {c.key for c in mapper.attrs}
    if "created_by" in valid_cols:
        return "created_by"
    return "user_id"


# ---------------------------------------------------------
# 1. Fetch User's Submitted Visits
# ---------------------------------------------------------
@router.get(
    "/my",
    response_model=List[SalesVisitResponse],
)
@router.get(
    "/my/",
    response_model=List[SalesVisitResponse],
)
async def get_my_sales_visits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        user_col = get_user_column_name()
        query = (
            select(SalesVisit)
            .where(getattr(SalesVisit, user_col) == current_user.id)
            .order_by(SalesVisit.id.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user sales visits: {str(exc)}",
        )


# ---------------------------------------------------------
# 2. Fetch All Visits (Admin / Manager)
# ---------------------------------------------------------
@router.get(
    "",
    response_model=List[SalesVisitResponse],
)
@router.get(
    "/",
    response_model=List[SalesVisitResponse],
)
async def get_sales_visits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    try:
        query = select(SalesVisit).order_by(SalesVisit.id.desc())
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving all sales visits: {str(exc)}",
        )


# ---------------------------------------------------------
# 3. Create Sales Visit
# ---------------------------------------------------------
@router.post(
    "",
    response_model=SalesVisitResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=SalesVisitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sales_visit(
    request: SalesVisitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payload = request.model_dump()

        clean_date = parse_date_safely(payload.get("visit_date"))
        clean_time = parse_time_safely(payload.get("visit_time"))

        count_query = select(func.count(SalesVisit.id))
        count_res = await db.execute(count_query)
        current_count = count_res.scalar() or 0
        report_number = f"SR-{current_count + 1:04d}"

        mapper = inspect(SalesVisit)
        valid_columns = {c.key for c in mapper.attrs}
        user_col = get_user_column_name()

        insert_data = {
            k: v for k, v in payload.items()
            if k in valid_columns and k not in ["id", "created_at", "updated_at"]
        }
        insert_data[user_col] = current_user.id
        insert_data["visit_date"] = clean_date
        insert_data["visit_time"] = clean_time

        if "report_number" in valid_columns and not insert_data.get("report_number"):
            insert_data["report_number"] = report_number

        if "estimated_quote" in insert_data:
            insert_data["estimated_quote"] = Decimal(str(insert_data["estimated_quote"]))

        visit = SalesVisit(**insert_data)
        db.add(visit)
        await db.commit()
        await db.refresh(visit)
        return visit

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while saving sales visit: {str(exc)}",
        )


# ---------------------------------------------------------
# 4. Get Single Sales Visit
# ---------------------------------------------------------
@router.get(
    "/{sales_visit_id}",
    response_model=SalesVisitResponse,
)
@router.get(
    "/{sales_visit_id}/",
    response_model=SalesVisitResponse,
)
async def get_sales_visit(
    sales_visit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(SalesVisit).where(SalesVisit.id == sales_visit_id)
    result = await db.execute(query)
    sales_visit = result.scalar_one_or_none()

    if not sales_visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales visit report not found.",
        )

    user_col = get_user_column_name()
    owner_id = getattr(sales_visit, user_col, None)

    role_name = getattr(current_user, "role", None)
    role_str = getattr(role_name, "name", str(role_name)).upper() if role_name else ""
    is_admin = current_user.is_superuser or "ADMIN" in role_str or "MANAGER" in role_str

    if not is_admin and owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this report.",
        )

    return sales_visit


# ---------------------------------------------------------
# 5. Update Sales Visit (PUT & PATCH)
# ---------------------------------------------------------
@router.put(
    "/{sales_visit_id}",
    response_model=SalesVisitResponse,
)
@router.put(
    "/{sales_visit_id}/",
    response_model=SalesVisitResponse,
)
@router.patch(
    "/{sales_visit_id}",
    response_model=SalesVisitResponse,
)
@router.patch(
    "/{sales_visit_id}/",
    response_model=SalesVisitResponse,
)
async def update_sales_visit(
    sales_visit_id: int,
    request: SalesVisitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(SalesVisit).where(SalesVisit.id == sales_visit_id)
    result = await db.execute(query)
    visit = result.scalar_one_or_none()

    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales visit report not found.",
        )

    user_col = get_user_column_name()
    owner_id = getattr(visit, user_col, None)

    role_name = getattr(current_user, "role", None)
    role_str = getattr(role_name, "name", str(role_name)).upper() if role_name else ""
    is_admin = current_user.is_superuser or "ADMIN" in role_str or "MANAGER" in role_str

    if not is_admin and owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this report.",
        )

    try:
        update_data = request.model_dump(exclude_unset=True)

        if "visit_date" in update_data and update_data["visit_date"]:
            update_data["visit_date"] = parse_date_safely(update_data["visit_date"])
        if "visit_time" in update_data and update_data["visit_time"]:
            update_data["visit_time"] = parse_time_safely(update_data["visit_time"])

        if "estimated_quote" in update_data and update_data["estimated_quote"] is not None:
            update_data["estimated_quote"] = Decimal(str(update_data["estimated_quote"]))

        mapper = inspect(SalesVisit)
        valid_columns = {c.key for c in mapper.attrs}

        for key, value in update_data.items():
            if key in valid_columns and key not in ["id", "created_by", "user_id", "created_at"]:
                setattr(visit, key, value)

        if "updated_at" in valid_columns:
            visit.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(visit)
        return visit

    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while updating report: {str(exc)}",
        )


# ---------------------------------------------------------
# 6. Delete Sales Visit
# ---------------------------------------------------------
@router.delete(
    "/{sales_visit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@router.delete(
    "/{sales_visit_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sales_visit(
    sales_visit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    ),
):
    service = SalesVisitService(db)
    deleted = await service.delete(sales_visit_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales visit report not found.",
        )

    return None