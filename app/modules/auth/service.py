from datetime import datetime, timedelta, UTC
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.email import send_email, EmailSendError
from app.core.security import (
    create_access_token,
    verify_password,
    decode_access_token,
    hash_password,
)
from app.modules.auth.repository import AuthRepository


class AuthService:
    """
    Authentication business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AuthRepository(db)

    async def login(
        self,
        email: str,
        password: str,
    ) -> str:

        user = await self.repository.get_user_by_email(email)

        # If user does not exist (e.g. permanently deleted by admin)
        if user is None:
            raise ValueError("Invalid email or password.")

        # Check password first to verify authentic identity
        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password.")

        # If user account is marked inactive by admin
        if not user.is_active:
            raise ValueError("Account is inactive. Organization permission required to access this system.")

        user.last_login = datetime.now(UTC)

        await self.db.commit()

        return create_access_token(user.id)

    async def logout(
        self,
        token: str,
    ) -> None:

        payload = decode_access_token(token)

        if payload is None:
            raise ValueError(
                "Invalid or expired token."
            )

        jti = payload.get("jti")
        expires_at = payload.get("exp")

        if jti is None or expires_at is None:
            raise ValueError(
                "Invalid token payload."
            )

        existing_revoked_token = (
            await self.repository.is_token_revoked(jti)
        )

        if existing_revoked_token:
            raise ValueError(
                "Token has already been revoked."
            )

        await self.repository.revoke_token(
            jti=jti,
            expires_at=datetime.fromtimestamp(
                expires_at,
                tz=UTC,
            ),
        )

    async def forgot_password(
        self,
        email: str,
    ) -> None:

        user = await self.repository.get_user_by_email(email)

        if user is None:
            raise ValueError("No user found with this email address.")

        if not user.is_active:
            raise ValueError("Account is inactive. Organization permission required to access this system.")

        # Generate a secure 6-digit OTP
        otp = str(secrets.randbelow(900000) + 100000)

        # OTP expires after 10 minutes
        expires_at = datetime.now(UTC) + timedelta(minutes=10)

        # Invalidate all previous OTPs
        await self.repository.invalidate_user_otps(user.id)

        # Save the new OTP
        await self.repository.create_password_reset_otp(
            user_id=user.id,
            otp=otp,
            expires_at=expires_at,
        )

        subject = "Password Reset OTP"

        body = f"""
    Hello {user.first_name},

    You requested to reset your password.

    Your One-Time Password (OTP) is:

    {otp}

    This OTP will expire in 10 minutes.

    Do not share this OTP with anyone.

    If you did not request this password reset, please ignore this email.

    Regards,
    Evio Elevator
    """

        try:
            send_email(
                to_email=user.email,
                subject=subject,
                body=body,
            )

        except EmailSendError as exc:
            raise ValueError(
                "Unable to send OTP email. Please try again later."
            ) from exc

    async def verify_reset_otp(
        self,
        email: str,
        otp: str,
    ) -> None:

        user = await self.repository.get_user_by_email(email)

        if user is None:
            raise ValueError("No user found with this email address.")

        password_reset_otp = (
            await self.repository.get_valid_password_reset_otp(
                user_id=user.id,
                otp=otp,
            )
        )

        if password_reset_otp is None:
            raise ValueError("Invalid or already used OTP.")

        if password_reset_otp.expires_at < datetime.now(UTC):
            raise ValueError("OTP has expired.")

    async def reset_password(
        self,
        email: str,
        otp: str,
        new_password: str,
    ) -> None:

        user = await self.repository.get_user_by_email(email)

        if user is None:
            raise ValueError("No user found with this email address.")

        password_reset_otp = (
            await self.repository.get_valid_password_reset_otp(
                user_id=user.id,
                otp=otp,
            )
        )
        if password_reset_otp is None:
            raise ValueError("Invalid or already used OTP.")
        if password_reset_otp.expires_at < datetime.now(UTC):
            raise ValueError("OTP has expired.")
        user.password_hash = hash_password(new_password)
        await self.db.commit()
        await self.repository.mark_otp_as_used(
            password_reset_otp
        )