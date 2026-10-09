from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest,
    CurrentUserResponse,
)
from app.modules.auth.service import AuthService
from app.core.dependencies import get_current_user, oauth2_scheme
from app.modules.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        token = await service.login(
            email=request.email,
            password=request.password,
        )

        return LoginResponse(
            access_token=token,
        )

    except ValueError as exc:
        msg = str(exc)
        # Specific forbidden status if inactive
        if "Organization permission" in msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=msg,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )


# Dedicated endpoint specifically for Swagger Docs OAuth2 form authentication
@router.post("/swagger-token", response_model=LoginResponse, include_in_schema=False)
async def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        token = await service.login(
            email=form_data.username,
            password=form_data.password,
        )

        return LoginResponse(
            access_token=token,
        )

    except ValueError as exc:
        msg = str(exc)
        if "Organization permission" in msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=msg,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        await service.logout(token)

        return {
            "message": "Logged out successfully."
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Get the currently authenticated user's profile.
    """
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        await service.forgot_password(
            email=request.email,
        )

        return {
            "message": "Password reset OTP has been sent to your email."
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/verify-reset-otp")
async def verify_reset_otp(
    request: VerifyResetOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        await service.verify_reset_otp(
            email=request.email,
            otp=request.otp,
        )

        return {
            "message": "OTP verified successfully."
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)

    try:
        await service.reset_password(
            email=request.email,
            otp=request.otp,
            new_password=request.new_password,
        )

        return {
            "message": "Password reset successfully."
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )