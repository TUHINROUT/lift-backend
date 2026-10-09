from collections.abc import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.users.models import User
from app.modules.users.repository import UsersRepository

# Point to the dedicated Swagger OAuth2 form-data endpoint
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/swagger-token"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get the currently authenticated user and verify their account status.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    jti = payload.get("jti")
    if jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    auth_repository = AuthRepository(db)
    is_revoked = await auth_repository.is_token_revoked(jti)
    if is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked. Please log in again.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    repository = UsersRepository(db)
    user = await repository.get_user_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Immediately block and trigger auto-logout if an admin deactivates the user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Organization permission required to access this system.",
        )

    return user


def require_roles(
    *allowed_roles: str,
) -> Callable:
    """
    Dependency for role-based authorization.
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = (current_user.role.name if current_user.role else "").strip().upper()
        valid_roles = {str(r).strip().upper() for r in allowed_roles}
        if "EMPLOYEE" in valid_roles or "TECHNICIAN" in valid_roles:
            valid_roles.update({"EMPLOYEE", "TECHNICIAN"})
        if not current_user.role or user_role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return role_checker