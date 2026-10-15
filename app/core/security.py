import bcrypt
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from uuid import uuid4
from app.core.config import settings


def _truncate_to_bytes(password: str) -> bytes:
    """Safely encodes and truncates password to 72 bytes max for bcrypt."""
    if not password:
        return b""
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Hashes password using bcrypt directly."""
    pwd_bytes = _truncate_to_bytes(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


# Alias for backward compatibility if imported elsewhere
get_password_hash = hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies password using native bcrypt.checkpw, eliminating Passlib's 72-byte probe crash."""
    if not plain_password or not hashed_password:
        return False
    try:
        pwd_bytes = _truncate_to_bytes(plain_password)
        hash_bytes = hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    """Creates JWT access token."""
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
    """Decodes JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None