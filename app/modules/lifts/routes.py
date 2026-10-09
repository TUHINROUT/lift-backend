from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from app.storage.upload import save_file
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.modules.lifts.schemas import (
    LiftCreate,
    LiftResponse,
    LiftUpdate,
)
from app.modules.lifts.service import LiftService
from app.modules.users.models import User
from datetime import date
router = APIRouter(
    prefix="/lifts",
    tags=["Lifts"],
)


#! Create lift
@router.post(
    "",
    response_model=LiftResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lift(
    lift_code: str = Form(...),
    customer_id: int = Form(...),
    building_name: str = Form(...),
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),

    installation_date: date | None = Form(None),

    warranty: str | None = Form(None),
    amc: str | None = Form(None),
    lift_status: str | None = Form(None),

    capacity: str | None = Form(None),
    lift_type: str | None = Form(None),
    machine_type: str | None = Form(None),
    controller_type: str | None = Form(None),
    door_type: str | None = Form(None),

    stops: int | None = Form(None),
    floors: int | None = Form(None),

    manufacturer: str | None = Form(None),
    serial_number: str | None = Form(None),

    remarks: str | None = Form(None),

    drawing: UploadFile | None = File(None),

    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
):
    service = LiftService(db)

    try:
        drawing_path = None

        if drawing:
            drawing_path = await save_file(
                drawing,
                "lift_drawings",
            )

        request = LiftCreate(
            lift_code=lift_code,
            customer_id=customer_id,
            building_name=building_name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            installation_date=installation_date,
            warranty=warranty,
            amc=amc,
            status=lift_status,
            capacity=capacity,
            lift_type=lift_type,
            machine_type=machine_type,
            controller_type=controller_type,
            door_type=door_type,
            stops=stops,
            floors=floors,
            manufacturer=manufacturer,
            serial_number=serial_number,
            drawing=drawing_path,
            remarks=remarks,
        )

        return await service.create_lift(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Get all lifts
@router.get(
    "",
    response_model=list[LiftResponse],
)
async def get_lifts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN","MANAGER")),
):
    service = LiftService(db)
    return await service.get_lifts()


#! Get lift by ID
@router.get(
    "/{lift_id}",
    response_model=LiftResponse,
)
async def get_lift(
    lift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN","MANAGER")),
):
    service = LiftService(db)

    try:
        return await service.get_lift_by_id(lift_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Update lift
@router.put(
    "/{lift_id}",
    response_model=LiftResponse,
)
async def update_lift(
    lift_id: int,
    request: LiftUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN","MANAGER")),
):
    service = LiftService(db)

    try:
        return await service.update_lift(
            lift_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Activate lift
@router.patch(
    "/{lift_id}/activate",
    response_model=LiftResponse,
)
async def activate_lift(
    lift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN","MANAGER")),
):
    service = LiftService(db)

    try:
        return await service.activate_lift(lift_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Deactivate lift
@router.patch(
    "/{lift_id}/deactivate",
    response_model=LiftResponse,
)
async def deactivate_lift(
    lift_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN","MANAGER")),
):
    service = LiftService(db)

    try:
        return await service.deactivate_lift(lift_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )