from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.auth.models import RevokedToken, PasswordResetOTP
class AuthRepository:
    """
    Database operations related to authentication.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Return user by email.
        """

        stmt = select(User).where(User.email == email)

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def revoke_token(
        self,
        jti: str,
        expires_at,
    ) -> RevokedToken:
        revoked_token = RevokedToken(
            jti=jti,
            expires_at=expires_at,
        )

        self.db.add(revoked_token)

        await self.db.commit()
        await self.db.refresh(revoked_token)

        return revoked_token


    async def is_token_revoked(
        self,
        jti: str,
    ) -> bool:
        stmt = select(RevokedToken).where(
            RevokedToken.jti == jti
        )

        result = await self.db.execute(stmt)

        revoked_token = result.scalar_one_or_none()

        return revoked_token is not None


    async def invalidate_user_otps(
        self,
        user_id: int,
    ) -> None:
        """
        Mark all previous unused OTPs for a user as used.
        """

        stmt = (
            update(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user_id,
                PasswordResetOTP.is_used == False,
            )
            .values(is_used=True)
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def create_password_reset_otp(
        self,
        user_id: int,
        otp: str,
        expires_at: datetime,
    ) -> PasswordResetOTP:

        password_reset_otp = PasswordResetOTP(
            user_id=user_id,
            otp=otp,
            expires_at=expires_at,
            is_used=False,
        )

        self.db.add(password_reset_otp)

        await self.db.commit()
        await self.db.refresh(password_reset_otp)

        return password_reset_otp

    async def create_password_reset_otp(
        self,
        user_id: int,
        otp: str,
        expires_at: datetime,
    ) -> PasswordResetOTP:

        password_reset_otp = PasswordResetOTP(
            user_id=user_id,
            otp=otp,
            expires_at=expires_at,
            is_used=False,
        )

        self.db.add(password_reset_otp)

        await self.db.commit()
        await self.db.refresh(password_reset_otp)


    async def get_valid_password_reset_otp(
        self,
        user_id: int,
        otp: str,
    ) -> PasswordResetOTP | None:

        stmt = (
            select(PasswordResetOTP)
            .where(
                PasswordResetOTP.user_id == user_id,
                PasswordResetOTP.otp == otp,
                PasswordResetOTP.is_used.is_(False),
            )
            .order_by(PasswordResetOTP.created_at.desc())
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def mark_otp_as_used(
        self,
        password_reset_otp: PasswordResetOTP,
    ) -> None:

        password_reset_otp.is_used = True

        await self.db.commit()