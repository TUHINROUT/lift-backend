from datetime import datetime, timedelta, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.tracking.models import EmployeeLocation
from app.modules.tracking.schemas import (
    LocationPingRequest,
    EmployeeLiveLocationResponse,
)

router = APIRouter(tags=["Live Tracking & Employee History"])


# ---------------------------------------------------------
# 1. Ping from Mobile
# ---------------------------------------------------------
@router.post("/tracking/ping")
@router.post("/tracking/ping/")
async def receive_location_ping(
    payload: LocationPingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(EmployeeLocation).where(EmployeeLocation.user_id == current_user.id)
    result = await db.execute(stmt)
    loc_record = result.scalars().first()

    now = datetime.utcnow()
    mapper = inspect(EmployeeLocation)
    valid_cols = {c.key for c in mapper.attrs}

    if not loc_record:
        init_data = {
            "user_id": current_user.id,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "speed": payload.speed or 0.0,
            "heading": payload.heading or 0.0,
            "status": payload.status or "Active",
            "current_destination": payload.current_destination,
            "battery_level": payload.battery_level or 100,
            "updated_at": now,
        }
        if "location_name" in valid_cols:
            init_data["location_name"] = payload.location_name or "Bhubaneswar"

        loc_record = EmployeeLocation(**init_data)
        db.add(loc_record)
    else:
        loc_record.latitude = payload.latitude
        loc_record.longitude = payload.longitude
        loc_record.speed = payload.speed or 0.0
        loc_record.heading = payload.heading or 0.0
        loc_record.status = payload.status or loc_record.status
        if payload.current_destination:
            loc_record.current_destination = payload.current_destination
        if payload.battery_level is not None:
            loc_record.battery_level = payload.battery_level
        if "location_name" in valid_cols and payload.location_name:
            loc_record.location_name = payload.location_name
        loc_record.updated_at = now

    await db.commit()
    return {"status": "success", "synced_at": now}


# ---------------------------------------------------------
# 2. Live Telemetry
# ---------------------------------------------------------
@router.get("/tracking/live", response_model=List[EmployeeLiveLocationResponse])
@router.get("/tracking/live/", response_model=List[EmployeeLiveLocationResponse])
async def get_active_workforce_locations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recent_cutoff = datetime.utcnow() - timedelta(hours=24)
    stmt = (
        select(EmployeeLocation, User)
        .join(User, EmployeeLocation.user_id == User.id)
        .where(EmployeeLocation.updated_at >= recent_cutoff)
        .order_by(EmployeeLocation.updated_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    telemetry = []
    for loc, user in rows:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
        telemetry.append(
            EmployeeLiveLocationResponse(
                user_id=user.id,
                employee_code=getattr(user, "employee_code", f"EMP-{user.id:03d}"),
                name=name,
                latitude=loc.latitude,
                longitude=loc.longitude,
                location_name=getattr(loc, "location_name", None) or "Bhubaneswar",
                speed=loc.speed or 0.0,
                heading=loc.heading or 0.0,
                status=loc.status or "Active",
                current_destination=loc.current_destination,
                battery_level=loc.battery_level or 100,
                updated_at=loc.updated_at,
            )
        )
    return telemetry


# ---------------------------------------------------------
# 3. Employee History & Latest Aliases (Used by React Frontend)
# ---------------------------------------------------------
@router.get("/employee-tracking/employee/{employee_id}/latest")
@router.get("/tracking/employee/{employee_id}/latest")
async def get_employee_latest_location(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(EmployeeLocation, User)
        .join(User, EmployeeLocation.user_id == User.id)
        .where(EmployeeLocation.user_id == employee_id)
        .order_by(EmployeeLocation.updated_at.desc())
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        return {}

    loc, user = row
    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
    return {
        "id": loc.id,
        "employee_id": user.id,
        "employee_name": name,
        "latitude": loc.latitude,
        "longitude": loc.longitude,
        "location_name": getattr(loc, "location_name", None) or "Bhubaneswar",
        "speed": loc.speed,
        "heading": loc.heading,
        "status": loc.status,
        "battery_level": loc.battery_level,
        "battery_percentage": loc.battery_level,
        "updated_at": loc.updated_at.isoformat() if loc.updated_at else None,
        "recorded_at": loc.updated_at.isoformat() if loc.updated_at else None,
    }


@router.get("/employee-tracking/employee/{employee_id}")
@router.get("/tracking/history")
async def get_employee_tracking_history(
    employee_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(EmployeeLocation, User)
        .join(User, EmployeeLocation.user_id == User.id)
        .order_by(EmployeeLocation.updated_at.desc())
    )
    if employee_id:
        stmt = stmt.where(EmployeeLocation.user_id == employee_id)

    result = await db.execute(stmt)
    rows = result.all()

    records = []
    for loc, user in rows:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
        records.append({
            "id": loc.id,
            "employee_id": user.id,
            "employee_name": name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "location_name": getattr(loc, "location_name", None) or "Bhubaneswar",
            "speed": loc.speed,
            "heading": loc.heading,
            "status": loc.status,
            "battery_level": loc.battery_level,
            "battery_percentage": loc.battery_level,
            "updated_at": loc.updated_at.isoformat() if loc.updated_at else None,
            "recorded_at": loc.updated_at.isoformat() if loc.updated_at else None,
        })
    return records


@router.get("/employee-tracking/employee/{employee_id}/by-date")
async def get_employee_tracking_by_date(
    employee_id: int,
    tracking_date: date = Query(..., alias="tracking_date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_dt = datetime.combine(tracking_date, datetime.min.time())
    end_dt = datetime.combine(tracking_date, datetime.max.time())

    stmt = (
        select(EmployeeLocation, User)
        .join(User, EmployeeLocation.user_id == User.id)
        .where(
            EmployeeLocation.user_id == employee_id,
            EmployeeLocation.updated_at >= start_dt,
            EmployeeLocation.updated_at <= end_dt,
        )
        .order_by(EmployeeLocation.updated_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    records = []
    for loc, user in rows:
        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.email
        records.append({
            "id": loc.id,
            "employee_id": user.id,
            "employee_name": name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "location_name": getattr(loc, "location_name", None) or "Bhubaneswar",
            "speed": loc.speed,
            "heading": loc.heading,
            "status": loc.status,
            "battery_level": loc.battery_level,
            "battery_percentage": loc.battery_level,
            "updated_at": loc.updated_at.isoformat() if loc.updated_at else None,
            "recorded_at": loc.updated_at.isoformat() if loc.updated_at else None,
        })
    return records