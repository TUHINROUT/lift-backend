from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_roles
from app.db.session import get_db
from app.storage.upload import save_file
from app.modules.users.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.modules.users.service import UsersService
from app.modules.users.models import User

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


#! Create user
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    department_id: int | None = Form(None),
    designation_id: int | None = Form(None),
    role_id: int | None = Form(None),
    company_id: int | None = Form(None),
    profile_photo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = UsersService(db)

    try:
        profile_photo_path = None

        if profile_photo:
            profile_photo_path = await save_file(
                profile_photo,
                "profile_photos",
            )

        request = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            department_id=department_id,
            designation_id=designation_id,
            role_id=role_id,
            company_id=company_id,
            profile_photo=profile_photo_path,
        )

        return await service.create_user(request)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#! Get all users
@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    name: str | None = None,
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: AsyncSession = Depends(get_db),
):
    service = UsersService(db)
    if name:
        return await service.search_users(name)
    return await service.get_users()


#! Get user by ID
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_roles("ADMIN", "MANAGER")),
    db: AsyncSession = Depends(get_db),
):
    service = UsersService(db)

    try:
        return await service.get_user(user_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Toggle user active status
@router.patch(
    "/{user_id}/toggle-status",
    response_model=UserResponse,
)
async def toggle_user_status(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = UsersService(db)

    try:
        return await service.toggle_user_status(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Activate user
@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = UsersService(db)

    try:
        return await service.activate_user(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Deactivate user
@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = UsersService(db)

    try:
        return await service.deactivate_user(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Update user (form data)
@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    employee_code: str | None = Form(None),
    company_id: int | None = Form(None),
    department_id: int | None = Form(None),
    designation_id: int | None = Form(None),
    role_id: int | None = Form(None),
    is_active: bool | None = Form(None),
    is_verified: bool | None = Form(None),
    is_superuser: bool | None = Form(None),
    profile_photo: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = UsersService(db)

    try:
        profile_photo_path = None
        if profile_photo:
            profile_photo_path = await save_file(
                profile_photo,
                "profile_photos",
            )
        request = UserUpdate(
            first_name=first_name,
            last_name=last_name,
            employee_code=employee_code,
            company_id=company_id,
            department_id=department_id,
            designation_id=designation_id,
            role_id=role_id,
            profile_photo=profile_photo_path,
            is_active=is_active,
            is_verified=is_verified,
            is_superuser=is_superuser,
        )

        return await service.update_user(
            user_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


#! Delete user
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN")),
):
    service = UsersService(db)

    try:
        await service.delete_user(user_id)
        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )