from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC

from jose import JWTError, jwt
from uuid import uuid4
from app.core.config import settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )

def create_access_token(user_id: int) -> str:
    """
    Create JWT access token.
    """

    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "jti": str(uuid4()),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

def decode_access_token(token: str) -> dict | None:
    """
    Decode JWT token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload

    except JWTError:
        return None